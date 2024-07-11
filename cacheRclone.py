import os
import psutil
from plexapi.server import PlexServer, CONFIG
from plexapi.exceptions import NotFound
from plexapi.video import Episode, Movie, Show
import logging
import subprocess
import sys

# Constants for ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Input Configuration
PLEX_URL = 'http://x.x.x.x:32400'
PLEX_TOKEN = 'xxxxxxxxxxxx'
LOG_FILENAME = 'plex_cache.log'
LOG_LEVEL = logging.INFO

# Determine if the output is a TTY (i.e., a terminal)
USE_COLOR = sys.stdout.isatty()

def configure_logging():
    """
    Configures logging to both a file and the console.
    """
    logging.basicConfig(
        filename=LOG_FILENAME, 
        level=LOG_LEVEL, 
        format='%(asctime)s %(levelname)s: %(message)s'
    )
    if USE_COLOR:
        # Also log to console with color if output is a terminal
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        logging.getLogger().addHandler(console_handler)

def connect_to_plex():
    """
    Connects to the Plex server using the provided URL and token.
    Returns the PlexServer instance.
    """
    try:
        plex_url = PLEX_URL or CONFIG.data['auth'].get('server_baseurl')
        plex_token = PLEX_TOKEN or CONFIG.data['auth'].get('server_token')

        plex = PlexServer(plex_url, plex_token)
        logging.info(f"Connected to Plex server at: {plex_url}")
        return plex

    except Exception as e:
        logging.error(f"Error connecting to Plex server: {e}")
        raise SystemExit(1)

def get_total_episodes(plex, show, seasonNumber, episodeSection):
    """
    Fetches the total number of episodes for a given show and season.
    """
    try:
        episodes = plex.library.section(episodeSection).get(show).episodes()
        total_episodes = sum(1 for ep in episodes if ep.seasonNumber == seasonNumber)
        logging.debug(f"Total episodes for {show} season {seasonNumber}: {total_episodes}")
        return total_episodes
    except Exception as e:
        logging.error(f"Error in get_total_episodes for show {show}, season {seasonNumber}: {e}")
        return 0

def get_next_episode(plex, show, seasonNumber, episodeNumber, episodeSection):
    """
    Fetches the next episode to be played for a given show, season, and current episode number.
    """
    try:
        episodes = plex.library.section(episodeSection).get(show).episodes()
        next_episodes = [ep for ep in episodes if ep.seasonNumber == seasonNumber and ep.index > episodeNumber]
        if next_episodes:
            next_ep = min(next_episodes, key=lambda ep: ep.index)
            logging.debug(f"Next episode for {show} S{seasonNumber}E{episodeNumber}: S{next_ep.seasonNumber}E{next_ep.index}")
            return next_ep
        return None
    except Exception as e:
        logging.error(f"Error in get_next_episode for show {show}, season {seasonNumber}, episode {episodeNumber}: {e}")
        return None

def is_rclone_caching(file_path):
    """
    Checks if rclone is currently caching a given file.
    """
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'rclone' in proc.info['name'] and 'md5sum' in proc.info['cmdline'] and file_path in proc.info['cmdline']:
                logging.info(f"Found rclone process already caching: {file_path}")
                return True
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logging.error(f"Error checking rclone process for file {file_path}: {e}")
        return False

def start_rclone_cache(file_path):
    """
    Starts rclone caching for a given file.
    """
    try:
        logging.info(f"Starting cache of {file_path}")
        subprocess.Popen(['rclone', 'md5sum', file_path])
    except Exception as e:
        logging.error(f"Error starting rclone cache for file {file_path}: {e}")

def log_system_usage():
    """
    Logs the current system's CPU and memory usage.
    """
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    logging.info(f"System CPU Usage: {cpu_usage}%")
    logging.info(f"System Memory Usage: {memory_info.percent}% used, {memory_info.available // (1024 * 1024)}MB available")

def main():
    configure_logging()
    log_system_usage()
    plex = connect_to_plex()
    
    logging.info('Script execution started')
    currentlyPlaying = plex.sessions()

    shows_list = []
    movies_list = []
    warnings_list = []

    for session in currentlyPlaying:
        try:
            if isinstance(session, Episode):
                show = session.grandparentTitle if isinstance(session, Episode) else session.show().title
                seasonNumber = session.parentIndex if hasattr(session, 'parentIndex') else "Unknown"
                episodeNumber = session.index if hasattr(session, 'index') else "Unknown"
                episode_title = session.title
                episodeSection = session.librarySectionTitle
                user = session.usernames[0] if session.usernames else "Unknown User"

                total_episodes = get_total_episodes(plex, show, seasonNumber, episodeSection)
                if total_episodes == 0:
                    warning_message = f"No episodes found for {show} season {seasonNumber}"
                    logging.warning(warning_message)
                    warnings_list.append(warning_message)
                    continue

                log_message = (
                    f"Show: {show}\n"
                    f"Season: {seasonNumber} out of {session.show().parentIndex}\n"
                    f"Episodes: {episode_title} 3 out of {session.show().episodes}"
                )
                logging.info(log_message)
                shows_list.append(log_message)

                nextEp = get_next_episode(plex, show, seasonNumber, episodeNumber, episodeSection)

                if nextEp:
                    nextEpisodeNumber = nextEp.index
                    fileToCache = nextEp.media[0].parts[0].file
                    logging.info(f"Next Episode {nextEpisodeNumber}: {fileToCache}")

                    if is_rclone_caching(fileToCache):
                        logging.info(f"Skipping caching of {fileToCache} as it is already being cached")
                    else:
                        logging.info(f"Caching {fileToCache} now")
                        start_rclone_cache(fileToCache)

                else:
                    logging.info("Currently playing the last episode")

            elif isinstance(session, Movie):
                movie_name = session.title
                user = session.usernames[0] if session.usernames else "Unknown User"
                log_message = f"Movie: {movie_name}, User: {user}"
                logging.info(log_message)
                movies_list.append(log_message)

            elif isinstance(session, Show):
                show_name = session.title
                user = session.usernames[0] if session.usernames else "Unknown User"
                log_message = f"Show: {show_name}, User: {user}"
                logging.info(log_message)
                shows_list.append(log_message)

        except Exception as e:
            logging.error(f"Error processing session: {e}")
            continue

    # Log shows and movies separately
    if shows_list:
        logging.info("\nShows currently playing:")
        for show_log in shows_list:
            logging.info(show_log)

    if movies_list:
        logging.info("\nMovies currently playing:")
        for movie_log in movies_list:
            logging.info(movie_log)

    # Add empty lines after logging
    logging.info("\n\n")

    # Log warnings at the end
    if warnings_list:
        logging.warning("\nWarnings:")
        for warning in warnings_list:
            logging.warning(warning)

if __name__ == "__main__":
    main()
