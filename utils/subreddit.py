#!/usr/bin/python3

import json
import logging
import requests
log = logging.getLogger(__name__)

class Subreddit:

    def __init__(self, name, keywords, posts=[]):
        self.name = name
        self.keywords = keywords
        self.posts = posts
        self.filteredPosts = []
    
    def __init__(self, entries):
        self.__dict__.update(entries)

    def getNewPosts(self):
        log.info(f"Fetching posts from {self.name}")
        headers = {'User-agent': 'reddit-notifier'}
        try:
            response = requests.get(f"https://www.reddit.com/r/{self.name}/new.json", headers=headers)
        except Exception as e:
            log.error(f"Error fetching posts: {e}")
            raise SystemExit(e)

        if(response.status_code < 200 or response.status_code > 399):
            log.error(f"Request failed with status code: {response.status_code}")
            raise SystemExit()
        responseObject = response.json()

        self.posts = []
        # Extract post titles and urls to be filtered
        for child in responseObject['data']['children']:
            self.posts.append({'title': child['data']['title'], 
                               'url': child['data']['url'], 
                               'subreddit': self.name})
        
        return

    def filterPosts(self):
        self.filteredPosts = []
        for post in self.posts:
            for keyword in self.keywords:
                if (keyword.lower() in post['title'].lower()) and (post not in self.filteredPosts):
                    self.filteredPosts.append(post)
        return
