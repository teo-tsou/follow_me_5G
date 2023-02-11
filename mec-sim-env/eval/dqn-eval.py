import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Activation
from tensorflow.keras.optimizers import Adam
import gym
from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory

env = gym.make("mec_sim:mec_sim-v0")
agent_weights_path = "dqn-weights.h5f"
actions = env.action_space.n
states = env.observation_space.shape

def build_model(states, actions):
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + states))    
    model.add(Dense(24, activation='relu'))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    return model

def build_agent(model, actions):
    memory = SequentialMemory(limit=20000, window_length=1)
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05, nb_steps=100000)       
    dqn = DQNAgent(model=model, memory=memory, policy=policy, 
                  nb_actions=actions, nb_steps_warmup=80, target_model_update=20)
    return dqn

model = build_model(states, actions)
dqn = build_agent(model, actions)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])
dqn.load_weights(agent_weights_path)
_=dqn.test(env,nb_episodes=300,visualize=False)