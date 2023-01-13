from gym.envs.registration import register
register(
    id="mec_sim-v0",
    entry_point="mec_sim.envs:MecEnv",
)