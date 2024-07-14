import os
import psutil
from plexapi.server import PlexServer
from plexapi.video import Episode
import logging
import subprocess
import configparser
import time


# Load configuration
config = configparser.ConfigParser()

# Use the environment variable for config location
config_file = os.getenv('CONFIG_LOCATION', '/app/config/config.ini')

if not os.path.exists(config_file):
    print(f"Configuration file '{config_file}' not found.")
    raise SystemExit(1)

config.read(config_file)

try:
    PLEX_URL = config.get('Plex', 'PLEX_URL')
    PLEX_TOKEN = config.get('Plex', 'PLEX_TOKEN')
    LOG_FILE = config.get('Logging', 'LOG_FILE')
except configparser.NoSectionError as e:
    print(f"Configuration error: {e}")
    raise SystemExit(1)
except configparser.NoOptionError as e:
    print(f"Configuration error: {e}")
    raise SystemExit(1)

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Custom colors for different categories
COLORS = {
    'user': '\033[38;5;33m',        # Green for users
    'movie': '\033[38;5;166m',      # Orange for movies
    'show': '\033[38;5;63m',        # Blue for shows
    'current': '\033[38;5;201m',    # Red for currently playing
    'size': '\033[38;5;118m'        # Light green for sizes
}
RESET_COLOR = '\033[0m'  # Reset color

# Function to add ANSI color codes
def colorize(message, color_key):
    return f"{COLORS.get(color_key, '')}{message}{RESET_COLOR}"

# Check disk space before caching
def has_enough_disk_space(required_space_gb=5):
    try:
        statvfs = os.statvfs('/')
        available_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024 ** 3)
        logging.info(f"Available disk space: {available_space_gb:.2f} GB")
        return available_space_gb >= required_space_gb
    except Exception as e:
        logging.error(f"Error checking disk space: {e}")
        return False

# Connect to Plex server
try:
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    logging.info(f"Connected to Plex server at: {PLEX_URL}")
except Exception as e:
    logging.error(f"Error connecting to Plex server: {e}")
    raise SystemExit(1)

# Get total episodes for a show and season
def get_total_episodes(show, seasonNumber, episodeSection):
    try:
        episodes = plex.library.section(episodeSection).get(show).episodes()
        total_episodes = sum(1 for ep in episodes if ep.seasonNumber == seasonNumber)
        logging.debug(f"Total episodes for {show} season {seasonNumber}: {total_episodes}")
        return total_episodes
    except Exception as e:
        logging.error(f"Error in get_total_episodes: {e}")
        return 0

# Get next episode for a show and season
def get_next_episode(show, seasonNumber, episodeNumber, episodeSection):
    try:
        episodes = plex.library.section(episodeSection).get(show).episodes()
        next_episodes = [ep for ep in episodes if ep.seasonNumber == seasonNumber and ep.index > episodeNumber]
        if next_episodes:
            next_ep = min(next_episodes, key=lambda ep: ep.index)
            logging.debug(f"Next episode for {show} S{seasonNumber}E{episodeNumber}: S{next_ep.seasonNumber}E{next_ep.index}")
            return next_ep
        return None
    except Exception as e:
        logging.error(f"Error in get_next_episode: {e}")
        return None

# Check if rclone is already caching the file
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

# Start caching the file with rclone
def start_rclone_cache(file_path):
    try:
        if not has_enough_disk_space():
            logging.warning(f"Not enough disk space to cache {file_path}")
            return
        logging.info(f"Starting cache of {file_path}")
        subprocess.Popen(['rclone', 'md5sum', file_path])
    except Exception as e:
        logging.error(f"Error starting rclone cache: {e}")

# Calculate size of file in gigabytes
def get_file_size_gb(file_path):
    try:
        file_size_bytes = os.path.getsize(file_path)
        file_size_gb = file_size_bytes / (1024 ** 3)
        return file_size_gb
    except Exception as e:
        logging.error(f"Error getting file size: {e}")
        return 0

# Main script execution
if __name__ == "__main__":
    logging.info("Script execution started")

    try:
        currentlyPlaying = plex.sessions()
        shows_list = []
        movies_list = []

        for session in currentlyPlaying:
            try:
                if isinstance(session, Episode):
                    show = session.grandparentTitle
                    user = session.usernames[0] if session.usernames else "Unknown User"
                    seasonNumber = session.parentIndex
                    episodeNumber = session.index
                    episodeSection = session.librarySectionTitle

                    total_episodes = get_total_episodes(show, seasonNumber, episodeSection)
                    if total_episodes == 0:
                        warning = f"No episodes found for {show} season {seasonNumber}"
                        logging.warning(warning)
                        continue

                    log_message = f"Show: {colorize(show, 'show')}, User: {colorize(user, 'user')}, Season: {seasonNumber}, Episode: {episodeNumber}/{total_episodes}"
                    shows_list.append(log_message)
                    logging.info(log_message)

                    nextEp = get_next_episode(show, seasonNumber, episodeNumber, episodeSection)

                    if nextEp:
                        nextEpisodeNumber = nextEp.index
                        fileToCache = nextEp.media[0].parts[0].file
                        logging.info(f"Next Episode {nextEpisodeNumber}: {fileToCache}")

                        if is_rclone_caching(fileToCache):
                            logging.info(f"Skipping caching of {fileToCache} as it is already being cached")
                        else:
                            logging.info(f"Caching {fileToCache} now")

                            # Get file size in GB
                            file_size_gb = get_file_size_gb(fileToCache)
                            if file_size_gb > 0:
                                logging.info(f"Space needed for caching: {file_size_gb:.2f} GB")
                                start_rclone_cache(fileToCache)
                            else:
                                logging.warning(f"Failed to get file size for {fileToCache}")

                    else:
                        logging.info("Currently playing the last episode")
                else:
                    movie_name = session.title
                    user = session.usernames[0] if session.usernames else "Unknown User"
                    log_message = f"Movie: {colorize(movie_name, 'movie')}, User: {colorize(user, 'user')}"
                    movies_list.append(log_message)
                    logging.info(log_message)

            except Exception as e:
                logging.error(f"Error processing media: {e}")
                continue

        # Log summary of all media
        if shows_list or movies_list:
            if shows_list:
                logging.info(f"\nCurrently playing {len(shows_list)} {'show' if len(shows_list) == 1 else 'shows'}")
                for show_log in shows_list:
                    logging.info(show_log)

            if movies_list:
                logging.info(f"\nCurrently playing {len(movies_list)} {'movie' if len(movies_list) == 1 else 'movies'}")
                for movie_log in movies_list:
                    logging.info(movie_log)
        else:
            logging.info("\nNo media currently playing.")

    except Exception as e:
        logging.error(f"Error during script execution: {e}")

    logging.info('\n' * 3)
    logging.info("Script execution finished")
