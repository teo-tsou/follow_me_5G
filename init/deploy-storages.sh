#!/bin/bash
#Install Local-Path & NFS Provisioner
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/ && helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner --set nfs.server=k8s-master1 --set nfs.path=/var/lib/kubelet/migration/
#Install Multus CNI
git clone https://github.com/intel/multus-cni.git && cd multus-cni
cat ./deployments/multus-daemonset.yml | kubectl apply -f -


