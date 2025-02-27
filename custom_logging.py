import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure the logs directory exists
log_dir = os.path.abspath('logs')
os.makedirs(log_dir, exist_ok=True)

# Define log file path
log_file = os.path.join(log_dir, 'app.log')

# Prevent adding multiple handlers if this script is imported
if not logging.getLogger().hasHandlers():
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler with rotation (5MB per file, keep last 3 logs)
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setFormatter(log_formatter)

    # Console handler for real-time logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # Configure root logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Logging functions
def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def log_warning(message):
    logger.warning(message)

def log_debug(message):
    logger.debug(message)

# Example usage (Only runs if executed directly)
def test_logging():
    log_info("Application started.")
    log_warning("This is a warning message.")
    log_error("An error occurred.")
    log_debug("Debugging information.")

if __name__ == "__main__":
    test_logging()
