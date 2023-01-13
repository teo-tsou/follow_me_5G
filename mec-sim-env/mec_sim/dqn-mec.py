import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Activation
from tensorflow.keras.optimizers import Adam
import gym
from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory
from tensorflow.keras.callbacks import TensorBoard

tensorboard = TensorBoard(
    log_dir="C:\\Users\\teo-b\Documents\\Follow-Me Paper\\python-scripts\\mec-sim-env\\mec_sim\\logs6\\",
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
    memory = SequentialMemory(limit=20000, window_length=1)
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05, nb_steps=30000)       
    dqn = DQNAgent(model=model, memory=memory, policy=policy, 
                  nb_actions=actions, nb_steps_warmup=80, target_model_update=30)
    return dqn


dqn = build_agent(model, actions)
dqn.compile(Adam(lr=1e-3), metrics=['mae']) 
dqn.fit(env, nb_steps=30000, visualize=False, verbose=2, callbacks = [tensorboard])
dqn.save_weights("C:\\Users\\teo-b\Documents\\Follow-Me Paper\\python-scripts\\mec-sim-env\\mec_sim\\dqn_weights.h5f", overwrite=True)

#scores = dqn.test(env, nb_episodes=100, visualize=False)
#print(np.mean(scores.history['episode_reward']))

