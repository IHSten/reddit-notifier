#!/usr/bin/python3

import discord
import logging
import yaml
import inspect, os.path
import asyncio
import dotenv
import os

from utils.dbinterface import DBInterface
from utils.subreddit import Subreddit

subreddits = []

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
discordToken = ""
discordChannel = ""

db = DBInterface(os.path.join(path, 'posts.db'))
client = discord.Client(intents = discord.Intents.default())

def initializeLogging():
    logging.basicConfig(filename=os.path.join(path, "notifier.log"), level=logging.INFO, format='%(levelname)s : %(asctime)s - %(message)s')
    logging.info("Logger initialized")
    return

def readConfigs():
    dotenv.load_dotenv()
    logging.debug("Reading configs")
    subredditImport = []
    with open(os.path.join(path, 'configs/subreddits.yml'), 'r') as f:
        subredditImport = yaml.safe_load(f)['subreddits']

    for i, sub in enumerate(subredditImport):
        subreddits.append(Subreddit(sub))

    global discordToken
    discordToken = os.getenv('DISCORD_TOKEN')
    if not discordToken:
        logging.error(f"No Discord token provided. Exiting...")
        quit()
    
    global discordChannel
    discordChannel = os.getenv('DISCORD_CHANNEL')
    try:
        discordChannel = int(discordChannel)
    except:
        logging.error(f"No valid Discord channel ID provided. Exiting...")
        quit()

    logging.info(f"Finished reading configs. Acquired {len(subreddits)} subreddits.")
    return

def fetchSubPosts():
    for sub in subreddits:
        sub.getNewPosts()
        sub.filterPosts()
    return

def constructMessages():
    messages = []
    # check post titles against db
    notifiablePosts = db.checkPosts(subreddits)
    newPosts = len(notifiablePosts)
    logging.info(f"Found {newPosts} new posts to notify users about")
    
    if newPosts <= 0:
        return messages
    
    # insert new posts into db
    insertOperation = db.insertPosts(notifiablePosts)
    if not insertOperation:
        logging.error("Error inserting new posts into db failed.")
        raise SystemExit("db insert operation failed")
    
    for p in notifiablePosts:
        messages.insert(0, f"New post {p['title']} detected.")

    return messages

def notifyDiscord():
    client.run(discordToken)

async def sendMessage(message):
    channel = client.get_channel(discordChannel)
    await channel.send(message)
@client.event
async def on_ready():  #  Called when internal cache is loaded - we only want to send one message, so just do this here
    counter = 0
    for m in constructMessages():
        counter += 1
        await sendMessage(m)
    os._exit(0)

if __name__ == '__main__':
    initializeLogging()
    db.initializeDB()
    readConfigs()
    fetchSubPosts()
    notifyDiscord()
