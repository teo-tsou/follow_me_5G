# Installation Guide:

**Install NFS to Cluster through scripts:**

On the Master Node:

`root@master:~#  bash master-nfs.sh`

On the Worker Nodes:

```
root@base_station1:~# bash workers-nfs.sh

root@base_station2:~# bash workers-nfs.sh
```
Let’s ensure we can read/write to the shared directory. On one worker, touch a file:

`touch /mnt/nfs_client_files/ok.txt`

On another worker, look for the file:

`ls /mnt/nfs_client_files/ | grep ok.txt`

If the file exists, you’re good to go.

Deploy Storages (NFS Provisioner) & Network Plugins (Multus CNI):

On the Master Node:

`root@master:~# bash deploy-storages.sh`

## Install KubeVirt to the Cluster

- **Create the namespace**

`kubectl create namespace kubevirt`

- **Enable Live Migration**

`kubectl create configmap -n kubevirt kubevirt-config --from-literal feature-gates="LiveMigration"`

- **Deploy the KubeVirt operator** (version 0.54)

`kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/v0.54.0/kubevirt-operator.yaml`

- **Create the KubeVirt CR** (version 0.54)

`kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/v0.54.0/kubevirt-cr.yaml`

- **Wait until all KubeVirt pods come up**

`kubectl -n kubevirt wait kv kubevirt --for condition=Available --timeout=-1s`

- **Install virtctl with krew**

`kubectl krew install virt`
_Help command:_ `kubectl virt help`

- **Deploy the CDI operator** (version 1.51.0)

`kubectl apply -f https://github.com/kubevirt/containerized-data-importer/releases/download/v1.51.0/cdi-operator.yaml`

- **Deploy the CDI CDR** (version 1.51.0)

`kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/v1.51.0/cdi-cr.yaml`

- **Deploy the VNC Viewer** (Optional)

`kubectl create -f virt-vnc.yaml`
