import os
import logging

def has_enough_disk_space(required_space_gb=5):
    try:
        statvfs = os.statvfs('/')
        available_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024 ** 3)
        logging.info(f"Available disk space: {available_space_gb:.2f} GB")
        return available_space_gb >= required_space_gb
    except Exception as e:
        logging.error(f"Error checking disk space: {e}")
        return False

def get_file_size_gb(file_path):
    try:
        file_size_bytes = os.path.getsize(file_path)
        file_size_gb = file_size_bytes / (1024 ** 3)
        return file_size_gb
    except Exception as e:
        logging.error(f"Error getting file size: {e}")
        return 0
