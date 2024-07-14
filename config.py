import os
import configparser

def load_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)

    plex_url = os.getenv('PLEX_URL', config.get('Plex', 'PLEX_URL', fallback=None))
    plex_token = os.getenv('PLEX_TOKEN', config.get('Plex', 'PLEX_TOKEN', fallback=None))
    log_file = os.getenv('LOG_FILE', config.get('Logging', 'LOG_FILE', fallback='preCache.log'))

    if not plex_url or not plex_token:
        raise ValueError("Plex URL and Token must be set in the configuration file or as environment variables.")

    return plex_url, plex_token, log_file

def main():
    try:
        # Load configuration
        plex_url, plex_token, log_file = load_config()
        print(f"Loaded configuration - PLEX_URL: {plex_url}, PLEX_TOKEN: {plex_token}, LOG_FILE: {log_file}")

        # Other script logic using loaded configuration
        # Example:
        # Connect to Plex server, start logging, etc.

    except ValueError as ve:
        print(f"Configuration error: {ve}")
        raise SystemExit(1)

    except Exception as e:
        print(f"Error during script execution: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
