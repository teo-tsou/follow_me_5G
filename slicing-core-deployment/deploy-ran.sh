kubectl create -f ueransim.yaml 
#sleep 3;
#kubectl create -f oai-gnbsim1.yaml
#sleep 3;
#kubectl create -f oai-nr-ue1.yaml
sleep 3;
kubectl create -f oai-gnbsim2.yaml
sleep 3;
kubectl create -f oai-nr-ue2.yaml

