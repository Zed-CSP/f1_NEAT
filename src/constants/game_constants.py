# Display Settings
WIDTH = 1920
HEIGHT = 1080

# Car Settings
CAR_SIZE_X = 26
CAR_SIZE_Y = 26
INITIAL_POSITION = [1630, 140]
INITIAL_ANGLE = 135
DEFAULT_SPEED = 20
WHEELBASE = 20
MAX_STEERING_ANGLE = 30

# Colors
BORDER_COLOR = (255, 255, 255, 255)
RADAR_COLOR = (0, 255, 0)
TEXT_COLOR = (0, 0, 0)

# Checkpoints
CHECKPOINTS = [
    (1500, 336, 30),  # Starting area
    (360, 380, 32),   # First turn approach
    (1500, 980, 30),  # After first turn
    (1750, 400, 30),  # Mid track
]

# Simulation Settings
MAX_GENERATIONS = 1000
SIMULATION_TIMEOUT = 30 * 40  # 20 seconds worth of frames

# Reward Settings
CHECKPOINT_REWARD = 2000
WRONG_CHECKPOINT_PENALTY = -4000
TIME_PENALTY_FACTOR = -0.1

# Time Scale Settings
MIN_TIME_SCALE = 0.25
MAX_TIME_SCALE = 5.0
TIME_SCALE_INCREMENT = 0.25 