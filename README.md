# Manage-FTP-koukouli

Koukouli weather station uploads a ```.dat``` file every 5 minute to the FTP server.

Each ```.dat``` file contains 5 1-min measurements.

This script downloads the ```.dat``` files locally, and organizes them to to daily ```.csv``` files.

The generated ```.csv``` files are uploaded to the FTP server and archived to locally.

Both the remote and the loca raw ```.dat``` files are deleted after the ```.csv``` upload.



## Instructions

Edit the FTP parameters in ```ftp.py```. 

To avoid overlapping cron job execution, use ```flock``` in crontab:

```
*/10 * * * * /usr/bin/flock -w 0 ~/manage_ftp_koukouli.lock python3 ~/Manage-FTP-koukouli/main.py
```

To check if your cron job is running:

```
grep CRON /var/log/syslog
```
