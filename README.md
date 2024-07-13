# Plex Caching Script

## Overview

This script automates the caching of upcoming episodes from a Plex media server using rclone. It monitors currently playing media, identifies the next episodes to cache, checks disk space availability, and initiates caching processes accordingly.

## Features

- **Automatic Episode Caching**: Automatically identifies and caches upcoming episodes of TV shows being watched on Plex.
  
- **Logging and Monitoring**: Logs detailed information about currently playing media, caching operations, disk space availability, and errors.

- **Configuration**: Uses a `config.ini` file for easy customization of Plex server URL, API token, logging file path, and other settings.

## Requirements

- Python 3.6+
- `plexapi` library (`pip install plexapi`)
- `psutil` library (`pip install psutil`)

## Installation

1. **Clone the repository:**
- git clone https://github.com/drondeseries/plexCacherclonenextEpisode.git
- cd plexCacherclonenextEpisode


2. **Install dependencies:**

- pip install -r requirements.txt


3. **Configure `config.ini`:**

- Copy `config.example.ini` to `config.ini`.
- Update `PLEX_URL` and `PLEX_TOKEN` with your Plex server URL and API token.
- Adjust other settings as needed.

## Usage

- Run the script using Python:
- python main.py

## Running as a Cron Job
- To run the script automatically at scheduled intervals, follow these steps:
- Create a shell script (run_script.sh):
- Create a shell script that changes to the directory where main.py is located and then executes it.

<pre>
```bash
#!/bin/bash

# Change directory to where main.py is located
cd /path/to/plexPreCacherclonenextEpisode/

# Run the Python script
python3 main.py

```
</pre>
- Save this script and give it executable permissions:

<pre>
```
chmod +x run_script.sh 
```
</pre>

Edit the crontab:

Use crontab -e to edit your crontab file and schedule the execution of the shell script.

<pre>
```
*/15 * * * * /path/to/run_script.sh >> /path/to/logfile.log 2>&1

```
</pre>
- Replace /path/to/run_script.sh with the actual path to your run_script.sh file.

- This cron job will execute run_script.sh every 15 minutes.


### Logging

- Logs are stored in the specified `LOG_FILE` (configured in `config.ini`).
- Information about currently playing media, caching operations, errors, and warnings are logged.

## Contributing

Contributions are welcome! Feel free to fork the repository, open issues, and submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.








