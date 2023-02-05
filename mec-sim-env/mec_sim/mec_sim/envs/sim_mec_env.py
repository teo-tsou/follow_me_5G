import gym
from gym import spaces
import numpy as np
import time
from operator import itemgetter
import random
import threading

class MecEnv(gym.Env):
    def __init__(self):
        #super(MecEnv, self).__init__()
        #Actions
        self.action_space = spaces.Discrete(4)
        #Observations Array
        self.observation_space = spaces.Box(low=0, high=10000,shape=(7,), dtype=np.float64)
        self.nodes = {"10.64.45.45": {"name":"station01-b205", "cpu":0, "mem":0, "load":1, "mec":{"rtt":1}, "vms":""}, "10.64.45.46": {"name":"station02-b205", "cpu":0, "mem":0, "load":1, "mec":{"rtt":1}, "vms":""}, "10.64.45.220": {"name":"station03-b205", "cpu":0, "mem":0,"load":1, "mec":{"rtt":1},"vms":""}}
        self.nodes_to_ips = {"station01-b205":"10.64.45.45", "station02-b205":"10.64.45.46", "station03-b205":"10.64.45.220"}
        self.MAX_POS = 2
        self.APP = "sipp"
        self.lock = threading.Lock()
        self.min_load = 1.2
        self.max_load = 10
        self.min_rtt = 1.3
        self.max_rtt = 20
        self.rtt_factor = self.min_rtt/self.max_rtt
        self.load_factor = self.min_load/self.max_load
        self.migration_time = 1
        self.rtt = 1
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
        self.hot_curr_node=1
        self.stop_flag = False
        self.STEP_LIMIT = 1500
        self.target_node = ""
        self.t0 = threading.Thread(target=self.rtt_scenario, args=(30000,10,60))
        self.t1 = threading.Thread(target=self.load_scenario, args=())
        self.t0.start()
        self.t1.start()
        self.reset()


    def rtt_scenario(self,distance=30000,step=10,maximum_latency=60):

        while self.stop_flag == False:
            #Emulating a big range of cars with different velocities in the Highway
            velocity = random.uniform(20,30)
            duration = distance/velocity
            total_steps = int(duration/step)
            d_rtt = maximum_latency/total_steps
            sleep_time_per_step=5

            #Initial-Additional Latency due to  
            delta_rtt_node1 = random.gauss(0.5, 0.1) + 1 
            delta_rtt_node2 = maximum_latency/2 + random.gauss(0.5, 0.1) +1
            delta_rtt_node3 = maximum_latency + random.gauss(0.5, 0.1) +1
            
            self.lock.acquire()
            try:
                self.nodes[self.nodes_to_ips["station01-b205"]]["mec"]["rtt"] = delta_rtt_node1
                self.nodes[self.nodes_to_ips["station02-b205"]]["mec"]["rtt"] = delta_rtt_node2
                self.nodes[self.nodes_to_ips["station03-b205"]]["mec"]["rtt"] = delta_rtt_node3
            finally:
                self.lock.release()

            #Total RTT changes
            total_steps  = int(duration/step)

            #1-Way
            for cur_step in range(total_steps):
                if cur_step < total_steps/2:
                    sign = 1
                else:
                    sign = -1

                delta_rtt_node1 =  delta_rtt_node1 + d_rtt
                delta_rtt_node2 =  delta_rtt_node2 - sign*d_rtt
                delta_rtt_node3 =  delta_rtt_node3 - d_rtt

                self.lock.acquire()
                try:
                    self.nodes[self.nodes_to_ips["station01-b205"]]["mec"]["rtt"] = delta_rtt_node1
                    self.nodes[self.nodes_to_ips["station02-b205"]]["mec"]["rtt"] = delta_rtt_node2
                    self.nodes[self.nodes_to_ips["station03-b205"]]["mec"]["rtt"] = delta_rtt_node3
                finally:
                    self.lock.release()

                # sleep
                time.sleep(sleep_time_per_step)

            #Return
            for cur_step in range(total_steps):
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
                    
                finally:
                    self.lock.release()
                # sleep
                time.sleep(sleep_time_per_step)     
        self.t0.stop()
 
    def load_scenario(self):
        cpu1_list=[]
        cpu2_list=[]
        cpu3_list=[]
        mem1_list=[]
        mem2_list=[]
        mem3_list=[]
        with open('cpu_mem_1.txt', 'r') as f1, open('cpu_mem_2.txt', 'r') as f2, open('cpu_mem_3.txt', 'r') as f3:
                # iterate over the lines
                for _ in range(500):
                    line1 = f1.readline()
                    line2 = f2.readline()
                    line3 = f3.readline()
                    # split the line by space to get a list of columns
                    cpu1, mem1 = line1.split()
                    cpu2, mem2 = line2.split()
                    cpu3, mem3 = line3.split()

                    cpu1_list.append(cpu1)
                    cpu2_list.append(cpu2)
                    cpu3_list.append(cpu3)
                    mem1_list.append(mem1)
                    mem2_list.append(mem2)
                    mem3_list.append(mem3)
                
        while self.stop_flag == False:
            mem_noise = random.gauss(0.05, 0.01)
            cpu_noise = random.gauss(0.05, 0.01)
            for i in range(400):
                cpu1 = cpu1_list[i]
                cpu2 = cpu2_list[i]
                cpu3 = cpu3_list[i]
                mem1 = mem1_list[i]
                mem2 = mem2_list[i]
                mem3 = mem3_list[i]

                cpu1 = float(cpu1)/100 + cpu_noise
                cpu2 = float(cpu2)/100 + cpu_noise
                cpu3 = float(cpu3)/100 + cpu_noise
                mem1 = float(mem1)/100 + mem_noise
                mem2 = float(mem2)/100 + mem_noise
                mem3 = float(mem3)/100 + mem_noise

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
                time.sleep(5)    
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

    def increasing_order_load_nodes(self):
        load = [] 
        for key in self.nodes:
            load.append(tuple([self.nodes[key]["name"], self.nodes[key]["load"]]))
            load.sort(key=itemgetter(1))
        return load

    def increasing_order_rtt_nodes(self):
        rtts = []
        for key in self.nodes:
            rtts.append(tuple([self.nodes[key]["name"], self.nodes[key]["mec"]["rtt"]]))
            rtts.sort(key=itemgetter(1))
        return rtts
 
    def step(self,action):
        reward = 0
        self.node = self.get_vm_node()
        self_mig = 0
        rtt_reward = 0
        load_reward = 0
        migration_penalty = 0

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
                self.done=True
                self_mig = 1
                
            else:
                self.vm_migrate(self.target_host,self.APP)
        
        self.node = self.get_vm_node()
        
        #Obtain observation vars and some usefull vars & lists
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
            rtt_list = self.increasing_order_rtt_nodes()
            load_list = self.increasing_order_load_nodes()
        finally:
            self.lock.release()   

        #Check the ranking position of the migrated-stayed node
        rtt_pos = [idx for idx, tup in enumerate(rtt_list) if tup[0] == self.node]
        rtt_pos = rtt_pos[0]
        load_pos = [idx for idx, tup in enumerate(load_list) if tup[0] == self.node]
        load_pos = load_pos[0]

        #Reward Function
        rtt_reward = (self.min_rtt/self.rtt) - (self.rtt/self.max_rtt) + (min_list_rtt/self.rtt) - (self.rtt/max_list_rtt)
        load_reward = (self.min_load/self.load) - (self.load/self.max_load) + (min_list_load/self.load) - (self.load/max_list_load)

        #SLA Violation - Terminate the episode.
        if self.rtt > self.max_rtt:
            self.done=True
            
        if self.load > self .max_load:
            self.done=True        

        #Global Reward
        reward = rtt_reward + load_reward - migration_penalty

        #This is for the self migration case
        if self_mig == 1:
            reward = -10
        
        observation = [float(self.hot_curr_node), float(self.curr_rtt1), float(self.curr_load1), float(self.curr_rtt2), float(self.curr_load2), float(self.curr_rtt3), float(self.curr_load3)]
        observation = np.array(observation)   
        #print(f"Observation: {observation}")
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
