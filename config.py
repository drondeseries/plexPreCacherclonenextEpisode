import os
import configparser

def load_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)

    plex_url = config.get('Plex', 'PLEX_URL', fallback=os.getenv('PLEX_URL'))
    plex_token = config.get('Plex', 'PLEX_TOKEN', fallback=os.getenv('PLEX_TOKEN'))
    log_file = config.get('Logging', 'LOG_FILE', fallback='preCache.log')

    if not plex_url or not plex_token:
        raise ValueError("Plex URL and Token must be set in the configuration file or as environment variables.")

    return plex_url, plex_token, log_file
