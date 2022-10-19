from functools import total_ordering
import subprocess
import time
import requests
import csv 

PROMETHEUS = 'http://10.64.94.81:32288/'

rtt_node_01 = "deploy/rtt-monitor-node01"
rtt_node_02 = "deploy/rtt-monitor-node02"
rtt_node_03 = "deploy/rtt-monitor-node03"

def rtt_per_node(time="2s", node_name="", prev_value=5):
    if node_name == "station01-b205":
        response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': f'avg_over_time(rtt_node01[{time}])'})
    elif node_name == "station02-b205":
        response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': f'avg_over_time(rtt_node02[{time}])'})
    elif node_name == "station03-b205":
        response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': f'avg_over_time(rtt_node03[{time}])'})

    else:
        return(-1)    

    results = response.json()['data']['result']
    for result in results:
        value = float(result['value'][1])

    try:
        return value
    except UnboundLocalError:
        print("Fell into the error. Going to return the previous value.")
        return prev_value

def init_csv(rtt_file="rtt_scenario.csv"):

    header_file = ['rtt_node1', 'rtt_node2', 'rtt_node3']
    
    with open(rtt_file, 'w', encoding='UTF8', newline='') as rtt:
        writer = csv.writer(rtt)

        # write the header
        writer.writerow(header_file)

def write_csv(rtt_file, rtt_node1, rtt_node2, rtt_node3):
    
    data_file = [rtt_node1, rtt_node2, rtt_node3]
    
    with open(rtt_file, 'a', encoding='UTF8', newline='') as rtt:
        writer = csv.writer(rtt)

        # write the data
        writer.writerow(data_file)


def scenario(duration=2000,distance=400,step=100, sleep_time=6):
    maximum_latency = 60
    remove_latency(rtt_node_01)
    remove_latency(rtt_node_02)
    remove_latency(rtt_node_03)
    init_latency("0ms", rtt_node_01)
    init_latency(str((maximum_latency+4)/2) + "ms", rtt_node_02)
    init_latency(str((maximum_latency+4)) + "ms", rtt_node_03)

    delta_rtt_node1 = 0
    delta_rtt_node2 = maximum_latency/2
    delta_rtt_node3 = maximum_latency

    time.sleep(sleep_time)

    total_steps  = int(duration/step)
    stathero_step = maximum_latency/total_steps

    rtt_node1 = 5
    rtt_node2 = maximum_latency/2
    rtt_node3 = maximum_latency
    for cur_step in range(total_steps):
        # kai gia tous 3 komvous:
        # - pairnoume tis proigoumenes times (se ms)
        rtt_node1 = rtt_per_node(time="5s", node_name="station01-b205", prev_value = rtt_node1)
        rtt_node2 = rtt_per_node(time="5s", node_name="station02-b205", prev_value = rtt_node2)
        rtt_node3 = rtt_per_node(time="5s", node_name="station03-b205", prev_value = rtt_node3)

        print("\n", cur_step)
        print("RTT Node 1:", rtt_node1, "ms")
        print("RTT Node 2:", rtt_node2, "ms")
        print("RTT Node 3:", rtt_node3, "ms")

        write_csv("rtt_scenario.csv", rtt_node1, rtt_node2, rtt_node3)        

        # - upologizoume tin timi me vasi tin proigoumeni
        if cur_step < total_steps/2:
            sign = 1
        else:
            sign = -1

        delta_rtt_node1 = delta_rtt_node1 + stathero_step
        delta_rtt_node2 = delta_rtt_node2 - sign*stathero_step
        delta_rtt_node3 = delta_rtt_node3 - stathero_step

        # - ftiaxnoume to string gia to value
        rtt_node1_str = str(delta_rtt_node1) + "ms"
        rtt_node2_str = str(delta_rtt_node2) + "ms"
        rtt_node3_str = str(delta_rtt_node3) + "ms"

        print("Delta RTT Node 1:", delta_rtt_node1, "ms")
        print("Delta RTT Node 2:", delta_rtt_node2, "ms")
        print("Delta RTT Node 3:", delta_rtt_node3, "ms")

        # - set_latency(value="0.1ms", node=rtt_node_01)
        set_latency(value=rtt_node1_str, node=rtt_node_01)
        set_latency(value=rtt_node2_str, node=rtt_node_02)
        set_latency(value=rtt_node3_str, node=rtt_node_03)

        # sleep
        time.sleep(sleep_time)

    for cur_step in range(total_steps):
        # kai gia tous 3 komvous:
        # - pairnoume tis proigoumenes times (se ms)
        rtt_node1 = rtt_per_node(time="5s", node_name="station01-b205", prev_value = rtt_node1)
        rtt_node2 = rtt_per_node(time="5s", node_name="station02-b205", prev_value = rtt_node2)
        rtt_node3 = rtt_per_node(time="5s", node_name="station03-b205", prev_value = rtt_node3)

        print("\n", cur_step)
        print("RTT Node 1:", rtt_node1, "ms")
        print("RTT Node 2:", rtt_node2, "ms")
        print("RTT Node 3:", rtt_node3, "ms")

        write_csv("rtt_scenario.csv", rtt_node1, rtt_node2, rtt_node3)        

        # - upologizoume tin timi me vasi tin proigoumeni
        if cur_step < total_steps/2:
            sign = 1
        else:
            sign = -1

        delta_rtt_node1 = delta_rtt_node1 - stathero_step
        delta_rtt_node2 = delta_rtt_node2 - sign*stathero_step
        delta_rtt_node3 = delta_rtt_node3 + stathero_step

        # - ftiaxnoume to string gia to value
        rtt_node1_str = str(delta_rtt_node1) + "ms"
        rtt_node2_str = str(delta_rtt_node2) + "ms"
        rtt_node3_str = str(delta_rtt_node3) + "ms"

        print("Delta RTT Node 1:", delta_rtt_node1, "ms")
        print("Delta RTT Node 2:", delta_rtt_node2, "ms")
        print("Delta RTT Node 3:", delta_rtt_node3, "ms")

        # - set_latency(value="0.1ms", node=rtt_node_01)
        set_latency(value=rtt_node1_str, node=rtt_node_01)
        set_latency(value=rtt_node2_str, node=rtt_node_02)
        set_latency(value=rtt_node3_str, node=rtt_node_03)

        # sleep
        time.sleep(sleep_time)



def set_latency(value="0.1ms", node=rtt_node_01):
    try:
        result = subprocess.check_output(['kubectl', 'exec', "-it", node, "tc", "qdisc", "change", "dev", "net1", "root", "netem", "delay", value ])
    except:
        pass

def init_latency(value="0.1ms", node=rtt_node_01):
    try:
        result = subprocess.check_output(['kubectl', 'exec', "-it", node, "tc", "qdisc", "add", "dev", "net1", "root", "netem", "delay", value ])
    except:
        pass

def remove_latency(node=rtt_node_01):
    try:
        result = subprocess.check_output(['kubectl', 'exec', "-it", node, "tc", "qdisc", "del", "dev", "net1", "root", "netem"])
    except:
        pass

if __name__ == "__main__":
    init_csv(rtt_file="rtt_scenario.csv")

    scenario()
    
