import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Activation
from tensorflow.keras.optimizers import Adam
import gym
from rl.agents.sarsa import SARSAAgent
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy
from tensorflow.keras.callbacks import TensorBoard

tensorboard = TensorBoard(
    log_dir="/home/ubuntu/follow_me_5g/mec-sim-env/mec_sim/sarsa",
    histogram_freq=0,
    write_graph=False,
    write_images=False,
    update_freq='epoch',
    profile_batch=0,
    embeddings_freq=0,
    embeddings_metadata=None
)

env = gym.make("mec_sim:mec_sim-v0")
actions = env.action_space.n
states = env.observation_space.shape


#Build the ANN
def build_model(states, actions):
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + states))    
    model.add(Dense(24, activation='relu'))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    return model

model = build_model(states, actions)
model.summary()

#Build the Model

def build_agent(model, actions):
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05, nb_steps=100000)      
    sarsa = SARSAAgent(model=model, nb_actions=actions, policy=policy)
    return sarsa

sarsa = build_agent(model, actions)
sarsa.compile(Adam(lr=1e-3), metrics=['mae'])
sarsa.fit(env, nb_steps=200000, visualize=False, verbose=2, callbacks = [tensorboard])
sarsa.save_weights("/home/ubuntu/follow_me_5g/mec-sim-env/mec_sim/sarsa.h5f", overwrite=True)