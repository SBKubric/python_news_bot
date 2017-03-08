import requests
import random
from threading import Thread
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from models import initialize_db, Post
from datetime import date
import datetime
import time


class NewsCollector:
    def __init__(self):
        self.engine: Engine = initialize_db()

    def make_request_to_vk(self, method: str, params: dict) -> dict:
        vk_api_url = 'https://api.vk.com/method/'
        response = requests.get('{}{}'.format(vk_api_url, method), params=params)
        return response.json()

    def get_yesterday_timestamp(self):
        today = datetime.date.fromtimestamp(int(time.time()))
        timedelta = datetime.timedelta(days=-1)
        yesterday = today + timedelta
        return int(time.mktime(yesterday.timetuple()))

    def generate_post_url(self, owner_id: int, post_id: int) -> str:
        return 'vk.com/wall{}_{}'.format(owner_id, post_id)

    def is_a_news_post(self, text: str) -> bool:
        text = text.lower()
        word_combinations_blacklist = [
            ['приглаш', 'обучени'],
            ['приглаш', 'курс'],
            ['курс программирования'],
            ['кож', 'цвет'],
            ['кож', 'размер'],
            ['кож', 'стил'],
            ['одежд'],
            ['обув'],
            ['#snake'],
            ['заказ', 'бесплатн'],
            ['недорог'],
            ['скидк'],
            ['с днём рождения'],
            ['#trianglesis'],
            ['заняти'],
            ['ваканси'],
        ]

        for combination in word_combinations_blacklist:
            match_count = 0
            for bad_word in combination:
                if bad_word in text:
                    match_count += 1
            if match_count == len(combination):
                return False
        return True

    def remove_old_posts(self):
        session: Session = sessionmaker(autoflush=True, bind=self.engine)()
        old_posts = session.query(Post).filter(Post.created_at < datetime.date.fromtimestamp(self.get_yesterday_timestamp()))
        for post in old_posts:
            session.delete(post)
        session.commit()
        session.close()

    def fetch_posts(self) -> list:
        newsfeed_search_params = {
            'q': '#python',
            'count': '1000',
            'start_time': self.get_yesterday_timestamp(),
        }
        response_json = self.make_request_to_vk('newsfeed.search', newsfeed_search_params)
        return response_json['response'][1:]

    def filter_posts(self, posts) -> list:
        filtered_posts = []
        session = sessionmaker(autoflush=False, bind=self.engine)()
        for post in posts:
            is_text_long_enough = len(post.get('text', '')) > 100
            is_post = post.get('post_type', None) == 'post'
            is_not_ad = post.get('marked_as_ads', None) == 0
            is_already_saved = session.query(Post).filter(Post.owner_id == post.get('owner_id', 0)).filter(Post.post_id == post.get('post_id', 0)).first()
            if is_text_long_enough and is_post and is_not_ad and self.is_a_news_post(post.get('text', '')) and not is_already_saved:
                filtered_posts.append(post)
        session.close()
        return filtered_posts

    def update_db(self, new_posts: list):
        session = sessionmaker(autoflush=False, bind=self.engine)()
        for post in new_posts:
            post_instance = Post()
            post_instance.post_id = post.get('id')
            post_instance.owner_id = post.get('owner_id')
            post_instance.likes_count = post.get('likes').get('count')
            post_instance.created_at = date.fromtimestamp(post.get('date'))
            post_instance.url = self.generate_post_url(post.get('owner_id'),
                                                       post.get('id'))
            post_instance.description = post.get('text', '')
            session.add(post_instance)
        session.commit()
        session.close()

    def get_random_fresh_post(self) -> Post:
        session: Session = sessionmaker(autoflush=True, bind=self.engine)()
        posts = session.query(Post).order_by(-Post.likes_count).all()[:100]
        session.close()
        return random.choice(posts)

    def collect_news(self):
        new_posts = self.fetch_posts()
        filtered_posts = self.filter_posts(new_posts)
        self.remove_old_posts()
        self.update_db(filtered_posts)
        print('Updated news')

    def start(self):
        collector_daemon = Thread(target=self.collect_news)
        collector_daemon.start()
        return self


def start_news_collector() -> NewsCollector:
    return NewsCollector().start()


if __name__ == '__main__':
    start_news_collector()
