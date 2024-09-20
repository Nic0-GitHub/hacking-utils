import os
from dotenv import load_dotenv


load_dotenv('.env')
SECRET_KEY = os.getenv("SECRET_KEY", '12-3456-7890')
LOGS_DIR = os.getenv('LOGS_DIR', './logs')
SEED = int(os.getenv('SEED', 12345))
