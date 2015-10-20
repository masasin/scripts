from collections import namedtuple
import json
import sys
import time

from bs4 import BeautifulSoup
import praw
import requests


Chapter = namedtuple("Chapter", "title url")

TGWP_INDEX_URL = ("https://forums.spacebattles.com/threads/"
                  "rwby-the-gamer-the-games-we-play-disk-five.341621/")
SUBS = ["TGWP"]
TITLE_FORMAT = "{i} - {title}"

with open("settings.json", "r") as settings_file:
    SETTINGS = json.load(settings_file)


class Updater(object):
    def __init__(self, url=TGWP_INDEX_URL, settings=SETTINGS, subs=SUBS,
                 formatter=TITLE_FORMAT):
        self.url = url
        self.settings = settings
        self.subs = subs
        self.formatter = formatter
        self.session = self._login()
        self.links = self._get_story_links()

    def run(self):
        while True:
            print(time.strftime("%Y-%m-%d %H:%M:%S"), end="    ")
            self.links = self._get_story_links()
            latest_post = self._get_latest_post()
            chapter_number = int(latest_post.title.partition(" - ")[0])
            new_post_count = len(self.links) - chapter_number

            if new_post_count > 0:
                print("A new chapter!")
                self._update_latest_link(new_post_count)
            else:
                print("No new chapters...")

            time.sleep(10*60)

    def _get_story_links(self):
        post = BeautifulSoup(requests.get(self.url).text).html.article
        post_title = post.div.text.splitlines()[1]

        links = []
        link = post.a
        while True:
            if link.text == ("On those who live to see old age in a profession "
                             "where most die young."):
                break
            links.append(Chapter(link.text, link.get("href")))
            if link.next_sibling.next_sibling.strip():
                if post_title == link.text:
                    post_title += " (Cont.)"
                links.append(Chapter(post_title, TGWP_INDEX_URL))
            link = link.find_next("a")
        return links

    def _login(self):
        session = praw.Reddit(user_agent=self.settings["user_agent"])
        session.set_oauth_app_info(self.settings["client_id"],
                                   self.settings["client_secret"],
                                   self.settings["redirect_uri"])
        session.set_access_credentials(self.settings["scope"],
                                       self.settings["access_token"],
                                       self.settings["refresh_token"])

        return session

    def _get_latest_post(self):
        for post in self.session.get_subreddit("tgwp").get_new():
            if post.author.name in ("masasin", "TGWP_Updater"):
                return post
            else:
                continue
        else:
            self.session.send_message("masasin",
                                      "TGWP_Updater problem",
                                      "Cannot get latest post")

    def _update_latest_link(self, count):
        new_chapters = self.links[-count:]
        for sub in self.subs:
            for i, link in zip(reversed(range(count)), new_chapters):
                submission = {"subreddit": sub,
                              "title": self.formatter
                                  .format(i=len(self.links) - i,
                                          title=link.title),
                              "url": link.url,
                              "resubmit": True}
                try:
                    self.session.submit(**submission)
                except praw.errors.RateLimitExceeded:
                    print("Waiting 10 minutes to submit.")
                    time.sleep(10*60)
                    self.session.submit(**submission)


def main():
    updater = Updater()
    updater.run()
    

if __name__ == "__main__":
    main()
