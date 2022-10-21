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

