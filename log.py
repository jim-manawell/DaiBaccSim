import logging
from datetime import datetime
import os

# Create a custom logger class
### Usage ###
# log = log("sim", level=logging.INFO)  
# log.info("msg")
# log.info("msg")
# log.debug("msg")
# log.warning("msg")
# log.error("msg")
# log.critical("msg")
class log(logging.Logger):
  def __init__(self, log_filename_prefix: str, level=logging.INFO):
    super().__init__(level)

    # Create log folder
    log_folder = "./logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    # Set log filename
    log_filename = datetime.now().strftime(log_filename_prefix + '_%Y_%m_%d.log')
    log_path = os.path.join(log_folder, log_filename)
    self.file_handler = logging.FileHandler(log_path, 'w+') #a, w+
    
    # Set the formatter for the file handler
    log_formatter = logging.Formatter(fmt='%(asctime)s UTC %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    self.file_handler.setFormatter(log_formatter)

    # Add the file handler to the logger
    self.addHandler(self.file_handler)