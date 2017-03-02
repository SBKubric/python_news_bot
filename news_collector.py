import requests
import json
import random
from threading import Thread
from time import sleep


class NewsCollector:
    def make_request_to_vk(self, method: str, params: dict) -> dict:
        vk_api_url = 'https://api.vk.com/method/'
        response = requests.get('{}{}'.format(vk_api_url, method), params=params)
        return response.json()

    def initialize_db(self) -> bool:
        return True

    def fetch_posts(self) -> list:
        newsfeed_search_params = {
            'q': 'python',
        }
        response_json = self.make_request_to_vk('newsfeed.search', newsfeed_search_params)
        return response_json['response'][1:]

    def process_fetched_posts(self, fetched_posts: list):
        saved_posts = None
        try:
            with open('db.json') as db_handler:
                saved_posts = json.load(db_handler)
        except FileNotFoundError:
            saved_posts = []
        finally:
            for post in fetched_posts:
                found = False
                for p in saved_posts:
                    if post['id'] == p['id']:
                        found = True
                if not found:
                    saved_posts.append(post)
            with open('db.json', mode='w') as db_handler:
                json.dump(saved_posts, db_handler)

    def update_db(self, new_posts: list) -> bool:
        pass

    def get_random_fresh_post(self) -> dict:
        with open('db.json') as db_handler:
            posts = json.load(db_handler)
        return random.choice(posts)

    def collect_news(self):
        new_posts = self.fetch_posts()
        self.process_fetched_posts(new_posts)
        sleep(3600)

    def start_news_collector(self):
        if not self.initialize_db():
            raise RuntimeError('Failed to initialize database. Aborting.')
        collector_daemon = Thread(target=self.collect_news)
        collector_daemon.start()
        return self


def start_news_collector() -> NewsCollector:
    return NewsCollector.start_news_collector()


if __name__ == '__main__':
    start_news_collector()
