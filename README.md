# reddit-notifier

## Intro

reddit-notifier (RN) is a simple script that uses the reddit API, an sqlite database, and a gmail account to notify users when posts containing specified keywords have been posted to specified subreddits. It was created with the idea of notifying users for sales on subs like buildapcsales.

## Setup

Setup is as easy as filling out the `configs/subreddits.yml` and `configs/email.yml`, and running the script. The script will automatically create an sqlite database `posts.db`. Given that the script only gathers the newest 25 posts and will not send an email for duplicate posts, it's designed to be run periodically on a short interval (sub-15 minutes). This could be done with a scheduler, or as recommended, a cronjob. An example crontab line is below

```

```