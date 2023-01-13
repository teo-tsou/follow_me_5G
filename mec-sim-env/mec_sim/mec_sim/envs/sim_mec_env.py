import gym
from gym import spaces
import numpy as np
import time
import numpy as np
import subprocess
from operator import itemgetter
import csv
import random
import threading
import os as os_file
  

class MecEnv(gym.Env):
    def __init__(self):
        #super(MecEnv, self).__init__()
        #Actions
        self.action_space = spaces.Discrete(4)
        #Observations Array
        self.observation_space = spaces.Box(low=0, high=400,shape=(7,), dtype=np.float64)
        self.nodes = {"10.64.45.45": {"name":"station01-b205", "cpu":0, "mem":0, "load":0, "mec":{"rtt":0}, "vms":""}, "10.64.45.46": {"name":"station02-b205", "cpu":0, "mem":0, "load":0, "mec":{"rtt":0}, "vms":""}, "10.64.45.220": {"name":"station03-b205", "cpu":0, "mem":0,"load":0, "mec":{"rtt":0},"vms":""}}
        self.nodes_to_ips = {"station01-b205":"10.64.45.45", "station02-b205":"10.64.45.46", "station03-b205":"10.64.45.220"}
        self.MAX_POS = 2
        self.APP = "sipp"
        self.lock = threading.Lock()
        self.min_load = 1
        self.max_load = 100
        self.min_rtt = 1
        self.max_rtt = 45
        self.rtt_factor = self.min_rtt/self.max_rtt
        self.load_factor = self.min_load/self.max_load
        self.migration_time = 3
        self.rtt = 0
        self.load = 1
        self.target_node = 0
        self.target_rtt = 0
        self.target_load = 0
        self.curr_rtt1 =  self.nodes[self.nodes_to_ips["station01-b205"]]["mec"]["rtt"]
        self.curr_load1 =  self.nodes[self.nodes_to_ips["station01-b205"]]["load"]
        self.curr_rtt2 =  self.nodes[self.nodes_to_ips["station02-b205"]]["mec"]["rtt"]
        self.curr_load2 =  self.nodes[self.nodes_to_ips["station02-b205"]]["load"]
        self.curr_rtt3 =  self.nodes[self.nodes_to_ips["station03-b205"]]["mec"]["rtt"]
        self.curr_load3 =  self.nodes[self.nodes_to_ips["station03-b205"]]["load"]
        self.init_vm_to_node()
        self.rtt_init()
        self.stop_flag = False
        self.STEP_LIMIT = 1500
        self.target_node = ""
        self.t0 = threading.Thread(target=self.rtt_scenario, args=(30000,10,60))
        self.t1 = threading.Thread(target=self.load_scenario, args=())
        self.t0.start()
        self.t1.start()
        self.reset()
        

    def init_vm_to_node(self):
        self.nodes[self.nodes_to_ips["station01-b205"]]["vms"] = self.APP   

    def rtt_init(self):

        value1 = random.uniform(3.28, 8.5)
        value2 = random.uniform(3.76, 7.12)
        value3 = random.uniform(3.11, 7.89)

        self.nodes[self.nodes_to_ips["station01-b205"]]["mec"]["rtt"] = value1
        self.nodes[self.nodes_to_ips["station02-b205"]]["mec"]["rtt"] = value2
        self.nodes[self.nodes_to_ips["station03-b205"]]["mec"]["rtt"] = value3
    
    def rtt_generate(self):

        value1 = random.uniform(3.28, 3.8)
        value2 = random.uniform(3.76, 4.12)
        value3 = random.uniform(3.11, 4.89)

        return value1,value2,value3    

    def rtt_scenario(self,distance=30000,step=10,maximum_latency=60):

        while self.stop_flag == False:

            velocity = random.uniform(19,30)
            duration = distance/velocity
            total_steps = int(duration/step)
            d_rtt = maximum_latency/total_steps
            sleep_time_per_step=4

            #Initial-Additional Latency due to shadowing(random loss) 
            value1,value2,value3= self.rtt_generate()
            
            self.lock.acquire()
            self.nodes[self.nodes_to_ips["station01-b205"]]["mec"]["rtt"] = value1
            self.nodes[self.nodes_to_ips["station02-b205"]]["mec"]["rtt"] = (value2 + maximum_latency)/2
            self.nodes[self.nodes_to_ips["station03-b205"]]["mec"]["rtt"] = value3 + maximum_latency
            self.lock.release()


            delta_rtt_node1 = random.uniform(0.1,0.9) + 1 
            delta_rtt_node2 = maximum_latency/2 + random.uniform(0.1,0.9) +1
            delta_rtt_node3 = maximum_latency + random.uniform(0.1,0.9) +1
            

            total_steps  = int(duration/step)

            for cur_step in range(total_steps):
                value1,value2,value3=self.rtt_generate()
                # kai gia tous 3 komvous:
                # - pairnoume tis proigoumenes times (se ms)

                # - upologizoume tin timi me vasi tin proigoumeni
                if cur_step < total_steps/2:
                    sign = 1
                else:
                    sign = -1

                delta_rtt_node1 =    delta_rtt_node1 + d_rtt
                delta_rtt_node2 =    delta_rtt_node2 - sign*d_rtt
                delta_rtt_node3 =    delta_rtt_node3 - d_rtt

                # print("Delta RTT Node 1:", delta_rtt_node1, "ms")
                # print("Delta RTT Node 2:", delta_rtt_node2, "ms")
                # print("Delta RTT Node 3:", delta_rtt_node3, "ms")

                # - set_latency(value="0.1ms", node=rtt_node_01)
                self.lock.acquire()
                try:
                    self.nodes[self.nodes_to_ips["station01-b205"]]["mec"]["rtt"] = delta_rtt_node1
                    self.nodes[self.nodes_to_ips["station02-b205"]]["mec"]["rtt"] = delta_rtt_node2
                    self.nodes[self.nodes_to_ips["station03-b205"]]["mec"]["rtt"] = delta_rtt_node3
                finally:
                    self.lock.release()

                # sleep
                time.sleep(sleep_time_per_step)

            for cur_step in range(total_steps):
                value1,value2,value3=self.rtt_generate()
                # kai gia tous 3 komvous:
                # - pairnoume tis proigoumenes times (se ms)

                # - upologizoume tin timi me vasi tin proigoumeni
                if cur_step < total_steps/2:
                    sign = 1
                else:
                    sign = -1

                delta_rtt_node1 =   delta_rtt_node1 - d_rtt
                delta_rtt_node2 =   delta_rtt_node2 - sign*d_rtt
                delta_rtt_node3 =   delta_rtt_node3 + d_rtt

                self.lock.acquire()
                try:
                    self.nodes[self.nodes_to_ips["station01-b205"]]["mec"]["rtt"] = delta_rtt_node1
                    self.nodes[self.nodes_to_ips["station02-b205"]]["mec"]["rtt"] = delta_rtt_node2
                    self.nodes[self.nodes_to_ips["station03-b205"]]["mec"]["rtt"] = delta_rtt_node3
                    self.lock.release()
                finally:
                # sleep
                    time.sleep(sleep_time_per_step)     
        self.t0.stop()

    def rtt_generate(self):

        value1 = random.uniform(3.28, 3.8)
        value2 = random.uniform(3.76, 4.12)
        value3 = random.uniform(3.11, 4.89)

        return value1,value2,value3    


    def load_generator(self):

        cpu1 = (random.randint(7,10))/100
        cpu2 = (random.randint(10,15))/100
        cpu3 = (random.randint(44,47))/100

        
        mem1 = (random.randint(10,15))/100
        mem2 = (random.randint(20,25))/100
        mem3 = (random.randint(34,36))/100


        load1 = (1/(1-float(cpu1))) * (1/(1-float(mem1))) 
        load2 = (1/(1-float(cpu2))) * (1/(1-float(mem2))) 
        load3 = (1/(1-float(cpu3))) * (1/(1-float(mem3)))

        return load1,load2,load3


    def load_scenario(self):

        dir = r"C:\Users\teo-b\Downloads\GCD_VMs.tar\GCD_VMs"

        node_list = ["station01-b205", "station02-b205", "station03-b205"]

        while self.stop_flag == False:
            # go to the specified directory
            os_file.chdir(dir)

            counter = 0

            # get all the files in the specified directory
            files = os_file.listdir()

            #sort the files
            files.sort()

            # loop through each file in the directory
            for file in files:
                # get the filename of the current file
                filename = file

                # open the file
                with open(file, "r") as f:
                    # read the file line by line
                    lines = f.readlines()

                # loop through the lines in groups of 3
                    for i in range(0, len(lines), 3):
                        # get the current group of 3 lines
                        group = lines[i:i+3]

                        # split the lines into two columns
                        cpu1, mem1 = group[0].strip().split()
                        cpu2, mem2 = group[1].strip().split()
                        cpu3, mem3 = group[2].strip().split()

                        cpu1 = float(cpu1)/100
                        cpu2 = float(cpu2)/100
                        cpu3 = float(cpu3)/100
                        mem1 = float(mem1)/100
                        mem2 = float(mem2)/100
                        mem3 = float(mem3)/100

                        counter += 1
                        print(f"The load counter is: {counter}")

                        if counter % 20 == 0:

                            print(f"CPU kai RAM ana node PRIN tis allages: Node1: {cpu1},{mem1}, Node2: {cpu2},{mem2}, Node3: {cpu3},{mem3}")
                            random_node = random.choice(node_list)
                            print()
                            print(f"The random node is: {random_node}")

                            if random_node == "station01-b205":
                                node_cpu = cpu1
                                node_mem = mem1

                            elif random_node == "station02-b205":
                                node_cpu = cpu2
                                node_mem = mem2

                            elif random_node == "station03-b205":
                                node_cpu = cpu3
                                node_mem = mem3   

                            if 0 <= node_cpu <= 0.4:

                                node_cpu = node_cpu + random.uniform(0.4,0.9)

                            elif 0.4 <= node_cpu <= 0.7:

                                node_cpu = node_cpu + random.uniform(0.1,0.5)

                            elif 0.7 <= node_cpu <= 1.0:
                                
                                node_cpu = node_cpu + random.uniform(0.1,0.3)
                                
                                
                            if 0 <= node_mem <= 0.2:

                                node_mem = node_mem + random.uniform(0.3,0.9)

                            elif 0.2 <= node_mem <= 0.5:

                                node_mem = node_mem + random.uniform(0.3,0.5)

                            elif 0.5 <= node_mem <= 1.0:
                                
                                node_mem = node_mem + random.uniform(0.1,0.4)                            
        
                            if random_node == "station01-b205":
                                cpu1 = node_cpu
                                mem1 = node_mem

                            elif random_node == "station02-b205":
                                cpu2 = node_cpu
                                mem2 = node_mem

                            elif random_node == "station03-b205":
                                cpu3 = node_cpu
                                mem3 = node_mem


                        if float(cpu1) >= 1.0:
                            cpu1 = 0.99
                        if float(cpu2) >= 1.0:
                            cpu2 = 0.99
                        if float(cpu3) >= 1.0:
                            cpu3 = 0.99


                        if float(mem1) >= 1.0:
                            mem1 = 0.99
                        if float(mem2) >= 1.0:
                            mem2 = 0.99
                        if float(mem3) >= 1.0:
                            mem3 = 0.99        
                        
                        load1 = (1/(1-float(cpu1))) * (1/(1-float(mem1))) 
                        load2 = (1/(1-float(cpu2))) * (1/(1-float(mem2))) 
                        load3 = (1/(1-float(cpu3))) * (1/(1-float(mem3)))

                        self.lock.acquire()
                        try: 
                            self.nodes[self.nodes_to_ips["station01-b205"]]["load"] = load1
                            self.nodes[self.nodes_to_ips["station02-b205"]]["load"] = load2
                            self.nodes[self.nodes_to_ips["station03-b205"]]["load"] = load3
                        finally:
                            self.lock.release()

                        if counter % 20 == 0:
                            print(f"CPU kai RAM ana node META tis allages: Node1: {cpu1},{mem1}, Node2: {cpu2},{mem2}, Node3: {cpu3},{mem3}")
                            time.sleep(random.uniform(90,140))
                        time.sleep(3)

        self.t1.stop()            


    def vm_migrate(self,target_node="",app=""):
        host_ip = self.nodes_to_ips[target_node]
        time.sleep(self.migration_time)
        self.lock.acquire()
        try:
            for key in self.nodes:
                if key != str(host_ip):
                    self.nodes[key]["vms"] = ""
                else:
                    self.nodes[host_ip]["vms"] = app
        finally:
            self.lock.release()                    

    
    def get_vm_node(self):
        self.lock.acquire()
        try:
            for key in self.nodes:
                if self.nodes[key]["vms"] != "":
                    return(self.nodes[key]["name"])
            return 0
        finally:
            self.lock.release()


    def init_vm_to_node(self):
        self.lock.acquire()
        try:
            self.nodes[self.nodes_to_ips["station01-b205"]]["vms"] = self.APP
        finally:
                self.lock.release()

    def get_vm_nf(self):
        self.lock.acquire()
        try:
            for key in self.nodes:
                if self.nodes[key]["vms"] != "":
                    return(self.nodes[key]["vms"])
            return 0
        finally:
                self.lock.release()             

    def get_the_current_rtt_node(self):
        for key in self.nodes:
            if self.nodes[key]["vms"] != "":
                return(self.nodes[key]["mec"]["rtt"])
        return -1     


    def get_the_current_vm_load(self):
        for key in self.nodes:
            if self.nodes[key]["vms"] != "":
                load = self.nodes[key]["load"] 
                return(load)
        return load


    def min_max_load_node_detect(self):
        loads = []
        for key in self.nodes:
            loads.append(tuple([self.nodes[key]["name"], self.nodes[key]["load"]]))
            max_loaded_node = max(loads,key=itemgetter(1))[1]
            min_loaded_node = min(loads,key=itemgetter(1))[1]
        return min_loaded_node, max_loaded_node

    def min_max_rrt_node_detect(self):
        rtts = []
        for key in self.nodes:
            rtts.append(tuple([self.nodes[key]["name"], self.nodes[key]["mec"]["rtt"]]))
            max_rtt_node = max(rtts,key=itemgetter(1))[1]
            min_rtt_node = min(rtts,key=itemgetter(1))[1]
        return min_rtt_node, max_rtt_node


    def step(self,action):
        reward = 0
        self.node = self.get_vm_node()
        rtt_reward = 0
        load_reward = 0



        # print(f"The action is {action}")
        # print(f"The load is {self.load}")
        # print(f"The rtt is {self.rtt}")

        #Apply Action
        if action == 0:
            self.target_host = ''

        if action == 1:
            self.hot_curr_node = 1
            self.target_host = "station01-b205"

        if action == 2:
            self.hot_curr_node = 2
            self.target_host = "station02-b205"

        if action == 3:
            self.hot_curr_node = 3
            self.target_host = "station03-b205"
            
        if action != 0:
            if self.node == self.target_host:
                reward = -self.rtt_factor
                self.done = True
            else:
                self.vm_migrate(self.target_host,self.APP)
             
        
        self.lock.acquire()
        try:
            self.curr_rtt1 =  self.nodes[self.nodes_to_ips["station01-b205"]]["mec"]["rtt"]
            self.curr_load1 =  self.nodes[self.nodes_to_ips["station01-b205"]]["load"]
            self.curr_rtt2 =  self.nodes[self.nodes_to_ips["station02-b205"]]["mec"]["rtt"]
            self.curr_load2 =  self.nodes[self.nodes_to_ips["station02-b205"]]["load"]
            self.curr_rtt3 =  self.nodes[self.nodes_to_ips["station03-b205"]]["mec"]["rtt"]
            self.curr_load3 =  self.nodes[self.nodes_to_ips["station03-b205"]]["load"]
            self.rtt = self.get_the_current_rtt_node()
            self.load = self.get_the_current_vm_load()
            min_list_rtt,max_list_rtt = self.min_max_rrt_node_detect()
            min_list_load,max_list_load = self.min_max_load_node_detect()
        finally:
            self.lock.release()




        rtt_reward = (self.min_rtt/self.rtt) - (self.rtt/self.max_rtt) + (min_list_rtt/self.rtt) - (self.rtt/max_list_rtt)
        load_reward = (self.min_load/self.load) - (self.load/self.max_load) + (min_list_load/self.load) - (self.load/max_list_load)

        if rtt_reward < 0:
            self.done = True
        
        reward = self.rtt_factor * rtt_reward + self.load_factor * load_reward           
        
        #write_csv()


        observation = [float(self.hot_curr_node), float(self.curr_rtt1), float(self.curr_load1), float(self.curr_rtt2), float(self.curr_load2), float(self.curr_rtt3), float(self.curr_load3)]
        observation = np.array(observation)
      

        print(f"Observation: {observation}")
        #print(f"Award: {reward}")    
        info = {}   
        #Return step information
        return observation, reward, self.done, info


    def render(self):
        pass

    def close(self):
        self.stop_flag = True       

    def reset(self):
        self.done = False
        curr_node =  self.get_vm_node()

        if curr_node == "station01-b205":
            self.hot_curr_node = 1
        elif curr_node == "station02-b205":
            self.hot_curr_node = 2
        elif curr_node == "station03-b205":
            self.hot_curr_node = 3


        self.lock.acquire()
        try:
            self.curr_rtt1 =  self.nodes[self.nodes_to_ips["station01-b205"]]["mec"]["rtt"]
            self.curr_load1 =  self.nodes[self.nodes_to_ips["station01-b205"]]["load"]
            self.curr_rtt2 =  self.nodes[self.nodes_to_ips["station02-b205"]]["mec"]["rtt"]
            self.curr_load2 =  self.nodes[self.nodes_to_ips["station02-b205"]]["load"]
            self.curr_rtt3 =  self.nodes[self.nodes_to_ips["station03-b205"]]["mec"]["rtt"]
            self.curr_load3 =  self.nodes[self.nodes_to_ips["station03-b205"]]["load"]
        finally:
            self.lock.release()

        
        observation = [float(self.hot_curr_node), float(self.curr_rtt1), float(self.curr_load1), float(self.curr_rtt2), float(self.curr_load2), float(self.curr_rtt3), float(self.curr_load3)]
        observation = np.array(observation)
        #print(observation)

        return observation