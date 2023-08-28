#!/usr/bin/python3

from datetime import datetime
import logging
log = logging.getLogger(__name__)
import sqlite3


class DBInterface:

    def __init__(self):
        self.path =""

    def __init__(self, path):
        self.path = path

    def connectToDB(self):
        try:
            conn = sqlite3.connect(f'file:{self.path}?mode=rw', uri=True)
        except sqlite3.OperationalError as e:
            log.error("Error connection to sqlite database")
            log.error(f"{e}")
            SystemExit(e)
        
        return conn

    def initializeDB(self):
        log.info("Attempting to initialize sqlite database")
        try:
            conn = sqlite3.connect(f'file:{self.path}.db?mode=rw', uri=True)
            log.debug("sqlite database exists")
            conn.execute(''' CREATE TABLE IF NOT EXISTS posts (
                            rowid INTEGER PRIMARY KEY,
                            title text PRIMARY KEY,
                            date text,
                            subreddit text,
                            url text)''')
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            log.debug("sqlite database does not exist. Creating now...")
            try:
                conn = sqlite3.connect(f'file:{self.path}?mode-rwc', uri=True)
                conn.execute(''' CREATE TABLE IF NOT EXISTS posts (
                                rowid INTEGER PRIMARY KEY,
                                title text UNIQUE,
                                date text,
                                subreddit text,
                                url text)''')
                conn.commit()
                conn.close()
            except sqlite3.OperationalError:
                log.error(f"Cannot create sqlite database at {self.path}. Exiting...")
                SystemExit(sqlite3.OperationalError)
        
        return

    def checkPosts(self, subreddits):
        notifiablePosts = []

        conn = self.connectToDB()

        for sub in subreddits:
            try:
                cur = conn.cursor()
                cur.execute(f'''SELECT title FROM posts WHERE subreddit = ?''', (f"{sub.name}",))

                titleList = cur.fetchall()

                # for some reason cur.fetchall() is returning the titles in the format
                # [(title1, ), (title2, )]
                titleList = list(map(lambda titleTuple: titleTuple[0], titleList))

            except Exception as e:
                log.error("Error reading post from database")
                log.error(e)

            for post in sub.filteredPosts:
                if post['title'] not in titleList:
                    notifiablePosts.append(post)
        
        conn.close()
        return notifiablePosts

    def insertPosts(self, posts):
        conn = self.connectToDB()
        error = False

        for post in posts:
            # titles are unique in the database, so an IntegrityError will occur if a title is duplicated
            try:
                conn.execute(f'''INSERT INTO posts (title,date,subreddit,url)
                                VALUES(?, ?, ?, ?);''', (post['title'], datetime.today().strftime('%Y-%m-%d'), post['subreddit'], post['url']))
                conn.commit()
            except sqlite3.IntegrityError as ie:
                log.warning("Duplicate post attempted to be added to database.")
                log.warning("This shouldn't have happened, but it isn't a problem")
            except Exception as e:
                log.error("Something bad happened when inserting a post to the database.")
                log.error(e)
                error = True
        
        conn.close()
        return not error