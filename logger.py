import logging
import os
from datetime import datetime

# Create logs folder
os.makedirs("logs", exist_ok=True)

# Log filename with date
log_file = f"logs/jarvis_{datetime.now().strftime('%Y%m%d')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        # Save to file
        logging.FileHandler(log_file, encoding='utf-8'),
        # Also show in terminal
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("JARVIS")


def log_info(msg):
    logger.info(msg)

def log_error(msg):
    logger.error(msg)

def log_warning(msg):
    logger.warning(msg)

def log_debug(msg):
    logger.debug(msg)

def log_success(msg):
    logger.info(f"✅ {msg}")

def log_user(msg):
    logger.info(f"👤 User: {msg}")

def log_jarvis(msg):
    logger.info(f"🤖 JARVIS: {msg}")