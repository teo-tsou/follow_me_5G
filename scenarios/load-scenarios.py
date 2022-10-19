import subprocess
import time
import threading


load_node_01 = "load-stresser-node01"
load_node_02 = "load-stresser-node02"
load_node_03 = "load-stresser-node03"


#Afto dinei 10 load (bad load)
#stress-ng -vm 3 --vm-bytes 60% -t 100

#Afto dinei 10 load (bad load)
#stress-ng -vm 3 --vm-bytes 80% -t 100

#Afto dinei average xamhlo (3.33 se xamhlo load nodes - 4.44 se nodes me idi load)
#stress-ng -vm 2 --vm-bytes 40% -t 10000

#Afto dinei 5.43 average  - 7.142 
#stress-ng -vm 2 --vm-bytes 80% -t 10000


def set_high_average_load(node=load_node_01, ram_value=80, num_of_vms = 2, timeout = "120s"):
    try:
        subprocess.check_call(['kubectl', 'exec', "-it", node, "--", "/bin/bash", "-c", f"stress-ng -vm {num_of_vms} --vm-bytes {str(ram_value)}% -t {timeout}"])
    except:
        print("den perase")
        pass


def set_low_average_load(node=load_node_01, ram_value=40, num_of_vms = 2, timeout = "120s"):
    try:
        subprocess.check_call(['kubectl', 'exec', "-it", node, "--", "/bin/bash", "-c", f"stress-ng -vm {num_of_vms} --vm-bytes {str(ram_value)}% -t {timeout}"])
    except:
        print("den perase")
        pass


def set_low_high_load(node=load_node_01, ram_value=60, num_of_vms = 3, timeout = "120s"):
    try:
        subprocess.check_call(['kubectl', 'exec', "-it", node, "--", "/bin/bash", "-c", f"stress-ng -vm {num_of_vms} --vm-bytes {str(ram_value)}% -t {timeout}"])
    except:
        print("den perase")
        pass


def set_high_high_load(node=load_node_01, ram_value=80, num_of_vms = 3, timeout = "120s"):
    try:
        subprocess.check_call(['kubectl', 'exec', "-it", node, "--", "/bin/bash", "-c", f"stress-ng -vm {num_of_vms} --vm-bytes {str(ram_value)}% -t {timeout}"])
    except:
        print("den perase")
        pass


def scenario():


    t0 = threading.Thread(target=set_high_average_load, args=(load_node_01, 30, 2, "240s"))
    t1 = threading.Thread(target=set_low_average_load, args=(load_node_02, 10, 2, "120s"))
    t0.start()
    t1.start()
    # t0.join()
    t1.join()


    t1 = threading.Thread(target=set_high_high_load, args=(load_node_02, 60, 3, "120s"))
    t2 = threading.Thread(target=set_low_high_load, args=(load_node_03, 10, 3, "120s"))
    t1.start()
    t2.start()
    t0.join()
    t1.join()
    t2.join()
    

if __name__ == "__main__":

    scenario()
