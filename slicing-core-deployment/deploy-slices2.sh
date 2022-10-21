kubectl create -f mysql.yaml 
sleep 6;
kubectl create -f oai-nssf.yaml 
sleep 6;
kubectl create -f oai-udr.yaml
sleep 6; 
kubectl create -f oai-udm.yaml 
sleep 6;
kubectl create -f oai-ausf.yaml
sleep 6; 
kubectl create -f oai-nrf-slice12.yaml
sleep 6;
kubectl create -f oai-nrf-slice3.yaml
sleep 6; 
kubectl create -f oai-amf.yaml 
sleep 6;
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
