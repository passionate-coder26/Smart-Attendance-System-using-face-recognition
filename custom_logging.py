import logging
import os

# Ensure the logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(filename='logs/app.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
