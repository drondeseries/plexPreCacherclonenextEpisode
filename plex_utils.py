from plexapi.server import PlexServer
import logging

def connect_to_plex(plex_url, plex_token):
    try:
        plex = PlexServer(plex_url, plex_token)
        logging.info(f"Connected to Plex server at: {plex_url}")
        return plex
    except Exception as e:
        logging.error(f"Error connecting to Plex server: {e}")
        raise

def get_total_episodes(plex, show, seasonNumber, episodeSection):
    try:
        episodes = plex.library.section(episodeSection).get(show).episodes()
        total_episodes = sum(1 for ep in episodes if ep.seasonNumber == seasonNumber)
        logging.debug(f"Total episodes for {show} season {seasonNumber}: {total_episodes}")
        return total_episodes
    except Exception as e:
        logging.error(f"Error in get_total_episodes: {e}")
        return 0

def get_next_episode(plex, show, seasonNumber, episodeNumber, episodeSection):
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
