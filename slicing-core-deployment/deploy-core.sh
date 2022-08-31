kubectl create -f mysql.yaml 
sleep 3;
kubectl create -f oai-nssf.yaml 
sleep 3;
kubectl create -f oai-udr.yaml
sleep 3; 
kubectl create -f oai-udm.yaml 
sleep 3;
kubectl create -f oai-ausf.yaml
sleep 3; 
kubectl create -f oai-nrf-slice12.yaml
sleep 3;
kubectl create -f oai-nrf-slice3.yaml
sleep 3; 
kubectl create -f oai-amf.yaml 
sleep 3;
kubectl create -f oai-smf-slice1.yaml 
sleep 3;
kubectl create -f oai-smf-slice2.yaml 
sleep 3;
kubectl create -f oai-smf-slice3.yaml 

