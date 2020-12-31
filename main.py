#!/usr/bin/python3

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib
import ssl
import yaml

from utils.dbinterface import DBInterface
from utils.subreddit import Subreddit

subreddits = []
senderEmail = dict()
recipientEmails = []
db = DBInterface('posts.db')

def initializeLogging():
    logging.basicConfig(filename="notifier.log", level=logging.INFO, format='%(levelname)s : %(asctime)s - %(message)s')
    logging.info("Logger initialized")
    return

def readConfigs():
    logging.debug("Reading configs")
    subredditImport = []
    with open('./configs/subreddits.yml', 'r') as f:
        subredditImport = yaml.safe_load(f)['subreddits']

    for i, sub in enumerate(subredditImport):
        subreddits.append(Subreddit(sub))

    with open('./configs/email.yml', 'r') as f:
        emailConfig = yaml.safe_load(f)
        recipientEmails.extend(emailConfig['to'])
        senderEmail.update(emailConfig['from'])
    
    logging.info(f"Finished reading configs. Acquired {len(subreddits)} subreddits and will notify {len(recipientEmails)} recipientEmails.")
    return

def fetchSubPosts():
    for sub in subreddits:
        sub.getNewPosts()
        sub.filterPosts()
    
    return

def emailNotifications():
    # check post titles against db
    notifiablePosts = db.checkPosts(subreddits)
    newPosts = len(notifiablePosts)
    logging.info(f"Found {newPosts} new posts to notify users about")
    
    if newPosts <= 0:
        return
    
    # insert new posts into db
    insertOperation = db.insertPosts(notifiablePosts)

    if not insertOperation:
        logging.error("Error inserting new posts into db failed.")
        logging.error("Raise an issue for this")
        raise SystemExit("db insert operation failed")
    
    # notifiablePosts contains the lists of posts to send to users

    message = MIMEMultipart("alternative")
    message["Subject"] = f"reddit-notifier has found {len(notifiablePosts)} deals"
    message["From"] = senderEmail['email']
    message["To"] = ','.join(recipientEmails)

    emailBody = ""
    htmlBody = "<ul>\n"
    for post in notifiablePosts:
        emailBody += f"{post['title'][0: 20 if len(post['title']) < 20 else len(post['title'])]}:{post['url']} in {post['subreddit']} \n"
        htmlBody += f"<li><a href={post['url']}>{post['title'][0: 20 if len(post['title']) < 20 else len(post['title'])]} in {post['subreddit']} \n"

    text = f"""\
    This is a notification from reddit-notifier to let you know about new posts from chosen subreddits

    {emailBody}"""

    html = f"""\
    <html>
        <body>
            This is a notification from reddit-notifier to let you know about new posts from chosen subreddits
            
            {htmlBody}
        </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(senderEmail['email'], senderEmail['password'])
        recipients = ','.join(recipientEmails)
        server.sendmail(senderEmail['email'], recipients, message.as_string())

def main():
    initializeLogging()
    db.initializeDB()
    readConfigs()
    fetchSubPosts()
    emailNotifications()

if __name__ == '__main__':
    main()