sudo modprobe 8021q
sudo vconfig add eno1 200
sudo ifconfig eno1.200 up
sudo brctl addbr br0
sudo brctl addif br0 eno1.200
ifconfig br0 up

