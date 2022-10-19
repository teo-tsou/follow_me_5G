# Installation Guide:

## Init the k8s cluster and build the PodMigration Operator

By following this [repo](https://github.com/SSU-DCN/podmigration-operator)

When done, Deploy Storages (NFS Provisioner) & Network Plugins (Multus CNI):

On the Master Node:

`root@master:~# bash init/deploy-storages.sh`


## Install Prometheus & Grafana to the cluster

- **Install Helm**

`root@master:~# bash curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3`

`root@master:~# chmod 700 get_helm.sh`

`root@master:~# ./get_helm.sh`

- **Add the latest helm repository - Add the Prometheus community helm chart**

`root@master:~# helm repo add stable https://charts.helm.sh/stable` 

`root@master:~# helm repo add prometheus-community https://prometheus-community.github.io/helm-charts` 


- **Install kube-prometheus-stack**

`root@master:~# helm install prometheus prometheus-community/kube-prometheus-stack` 


## Install KubeVirt to the Cluster

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

- **Deploy the VNC Viewer** (Optional)

`kubectl create -f virt-vnc.yaml`
