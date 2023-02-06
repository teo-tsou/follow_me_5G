# Service migration and edge selection for MEC in a cloud-native 5G environment:

## System Architecture:

<img src="https://github.com/teo-tsou/follow_me_5g/blob/main/slicing-core-deployment/mig-setup.drawio (22).png" width=60% height=60%>


## Edge-Cloud Installation Guide:


### Init the k8s cluster and build the PodMigration Operator

Follow the instructions of this [repo](https://github.com/SSU-DCN/podmigration-operator)

For easy replication use these hostnames:

```
master-node: k8s-master1
worker-node #1: station01-b205
worker-node #2: station02-b205
worker-node #3: station03-b205
```

When the cluster is initialized and the podmigration operator is succesfully deployed:

- **Deploy Storages (NFS Provisioner) & Network Plugins (Multus CNI):**

Configure the init/deploy-storages.sh file depending on your cluster configs.

On the Master Node:

`root@master:~# bash init/deploy-storages.sh`

- **Create the migration dedicated host (br0) interfaces**

On the Worker Nodes:

`root@worker1:~# bash init/net-conf.sh`

`root@worker2:~# bash init/net-conf.sh`

Before running this script, make sure that you use your VLAN IDs


### Install Prometheus/Grafana & K8s Metrics Server to the cluster

- **Install Helm**

`root@master:~# bash curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3`

`root@master:~# chmod 700 get_helm.sh`

`root@master:~# ./get_helm.sh`

- **Add the latest helm repository - Add the Prometheus community helm chart**

`root@master:~# helm repo add stable https://charts.helm.sh/stable` 

`root@master:~# helm repo add prometheus-community https://prometheus-community.github.io/helm-charts` 


- **Install kube-prometheus-stack**

`root@master:~# helm install prometheus prometheus-community/kube-prometheus-stack` 


- **Install k8s Metric Server**

`root@master:~# kubectl create -f init/components.yaml` 


### Install KubeVirt to the Cluster

- **Create the namespace**

`kubectl create namespace kubevirt`

- **Deploy the KubeVirt operator** (version 0.45)

`kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/v0.54.0/kubevirt-operator.yaml`

- **Create the KubeVirt CR** (version 0.45)

`kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/v0.54.0/kubevirt-cr.yaml`

- **Wait until all KubeVirt pods come up**

`kubectl -n kubevirt wait kv kubevirt --for condition=Available --timeout=-1s`

- **Install virtctl with krew**

Install krew first:
https://krew.sigs.k8s.io/docs/user-guide/setup/install/

`kubectl krew install virt`
_Help command:_ `kubectl virt help`

- **Deploy the CDI operator** (version 1.43.0)

`kubectl apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/v1.51.0/cdi-operator.yaml`

- **Deploy the CDI CDR** (version 1.43.0)

`kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/v1.51.0/cdi-cr.yaml`

- **Enable Live Migration**

`kubectl edit -n kubevirt kubevirt kubevirt`

Add the following (experiment with diffrent values for optimal migration time):

```
    apiVersion: kubevirt.io/v1
    kind: Kubevirt
    metadata:
      name: kubevirt
      namespace: kubevirt
    spec:
      configuration:
        developerConfiguration:
          featureGates:
          - LiveMigration
        migrations:
          parallelMigrationsPerCluster: 5
          parallelOutboundMigrationsPerNode: 2
          bandwidthPerMigration: 64Mi
          completionTimeoutPerGiB: 800
          progressTimeout: 150
          disableTLS: false
```

To check on how to trigger a live migration on a KubeVirt VM check this [guide](https://kubevirt.io/user-guide/operations/live_migration/)

- **Deploy the VNC Viewer** (Optional)

`root@master:~# kubectl create -f init/virt-vnc.yaml`


### Importing new VM image via CDI Operator

On the Master Node:

`root@master:~# kubectl create -f init/vm1-image-import.yaml`

This YAML file imports an Ubuntu 20.04 LTS Image Server to all the cluster nodes, via NFS external provisioned. If you want to change the VM Image, or the disk storage for this image, please configure.

If there's a need to create another VM, import a new image with different name:

`root@master:~# kubectl create -f init/vm2-image-import.yaml`


### Deploy the OAI 5G Multi-Slice Core Network

For the deployment of the 5G NFs there're two options:

- **Deploy everything as a Pod:**

`root@master:~# bash slicing-core-deployment/pods/deploy-all.sh`

This script deploys all the CNFs along with gNodeB/UERANSIM and OAI-5G-NR UE.

- **Deploy some NFs as VMs:**

The only way to live migrate the NFs (due to SCTP maintenance), is by nesting docker images to the KubeVirt VMs. But first, you need to configure the corresponding VMs with the corresponding interfaces and with the appropriate Data Volumes and then to create/deploy them to the cluster. We provide some templates. Please check /init/vm-nf1.yaml and /init/vm-nf2.yaml. 

In our experiment we deploy the AMF as a nested container on the VM by using docker-compose:


-  **First, Deploy all the core functions before the AMF:**

`root@master:~# bash slicing-core-deployment/pods/before-amf.sh`

- **Deploy the VM:**

`root@master:~# kubectl create -f slicing-core-deployment/pods/vm-oai-amf.yaml`

Check the status of the deployed VMI:

`root@master:~# kubectl get vmi`

- **Deploy the AMF inside the VM :**

First, clone the repo inside the VM and install Docker-Compose by:

`root@master:~# bash init/docker_install.sh`

Then, deploy the AMF by:

`root@master:~# docker-compose -f slicing-core-deployment/docker-compose/oai-amf-docker-compose.yaml up -d`

You can always check the logs of the container by:

`root@master:~# docker logs -f oai-amf`

-  **Deploy the remaining NFs after the AMF:**

`root@master:~# bash slicing-core-deployment/pods/after-amf.sh`

After deploying the gNodeB and the UE, check if they're both successfully attached to the AMF by the logs of the VM.

-  **Finally, Check the network connectivity:**

To check if there's connectivity between the core and the UE just enter inside the UE pod's container and ping the IP of the corresponding UPF. For example for the oai-nr-ue which is associated with the URRLC slice:

`root@oai-nr-ue:~# ping 12.1.1.129 `


### Deploy Applications

There're three options for applications:

a) Chat Server b) SIPp Server and c) VLC server

You can deploy them as pods or as VMs (for chat server for example):

`root@master:~# kubectl create -f chat-server.yaml`

To interact with apps you should install the client sides on the UE:

For the Chat Server run the clients on the UEs:

`root@oai-nr-ue:~# python3 ue/client.py`

`root@oai-ueransim:~# python3 ue/client.py`

For SIPp Server - Install the SIPp and run the client on the UE:

`root@oai-nr-ue:~# bash ue/install_sipp.sh`

`root@oai-nr-ue:~# sudo sipp -sn uac 192.168.70.145:1234`


## Deep Reinforcement Learning Instructions

### OpenAI Custom MDP Environment

- **Install the dependecies - Conda Environment :**

Install conda on your machine from [here](https://docs.anaconda.com/anaconda/install/linux/)

Create the pre-configured keras-rl2 conda environment by:

`conda env create -f /init/environment.yml`

and activate the environment by:

`conda activate keras-rl2`

- **Register the custom MecEnv environment :**

Register our custom digital-twin-driven OpenAI Gym MecEnv environment by:

`(keras-rl2) root@master:~/follow_me_5g/mec-sim-env# pip install -e mec_sim`

- **Configure the environment to your system requirments:**

For example you can change the RTT or Load Thresholds. You can also modify the car speeds, and the mem,cpu AWGN noises and migration times the environment file is located on: ~/follow_me_5g/mec-sim-env/mec_sim/mec_sim/envs/mec_sim_env.py

### DQN & DSQN Agents

We have implemented 2 DRL architctures for DQN and DSQN agents respectively. Both can be found at the corresponding paths in the repo:
~/follow_me_5g/mec-sim-env/mec_sim/dqn.py
~/follow_me_5g/mec-sim-env/mec_sim/dsqn.py

Feel free to change the hyperparameters that have been used, such as the replay-buffer size, the learning-rate, the DNN and it's architecture, etc..

- **Train the agents - Monitor with TensorBoard :**

To monitor the learning process of the agents, we have integrated the TensorBoard. Please change the tensorboard logdir accordingly. 

To train the agents run:



At the end of the training you should see similar plots in the TensorBoard:



### Evaluate in real-testbed

- **Replace the digital-twin environment with the real-one:**








