kubectl create -f oai-smf-slice1.yaml
sleep 6;
kubectl create -f oai-smf-slice2.yaml 
sleep 6;
kubectl create -f oai-smf-slice3.yaml 
sleep 6;
kubectl create -f oai-spgwu-slice1.yaml
sleep 6; 
kubectl create -f oai-spgwu-slice2.yaml 
sleep 6;
kubectl create -f oai-ext-dn.yaml 
sleep 6
kubectl create -f ueransim.yaml 
sleep 6;
kubectl create -f oai-gnbsim2.yaml
sleep 6;
kubectl create -f oai-nr-ue2.yaml

