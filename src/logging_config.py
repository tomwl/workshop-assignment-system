# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 16:49:49 2025

This is just a helper file so that a shared log can be created across modules

@author: tom
"""

import logging

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)         
 
# Prevent multiple handlers if the logger is configured multiple times
if not logger.handlers:
    # Create a file handler to log to a file
    file_handler = logging.FileHandler('logs/logfile.log', 'w', 'utf-8', logger.level)
    file_handler.setLevel(logging.INFO)

    # Define log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add file handler to logger
    logger.addHandler(file_handler)
    
def logging_cleanup():
    logger.handlers.clear()
    logging.shutdown()