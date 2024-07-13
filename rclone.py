import psutil
import subprocess
import logging

def is_rclone_caching(file_path):
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'rclone' in proc.info['name'] and 'md5sum' in proc.info['cmdline'] and file_path in proc.info['cmdline']:
                logging.info(f"Found rclone process already caching: {file_path}")
                return True
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logging.error(f"Error checking rclone process: {e}")
        return False

def start_rclone_cache(file_path):
    try:
        if not has_enough_disk_space():
            logging.warning(f"Not enough disk space to cache {file_path}")
            return
        logging.info(f"Starting cache of {file_path}")
        subprocess.Popen(['rclone', 'md5sum', file_path])
    except Exception as e:
        logging.error(f"Error starting rclone cache: {e}")
