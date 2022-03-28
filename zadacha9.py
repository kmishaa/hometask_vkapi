from collections import Counter
import vk_api
from datetime import datetime, date
from typing import Dict, Any
import pandas as pd
import calendar
import string
from typing import List

login = '' # логин при входе вк
password = '' # пароль

OWNER_ID = -88397640
POST_ID = 2590479
DOMAIN = 'https://vk.com/hse'

FILE = 'result_of_zadacha5.csv'

punctuation_tokens = string.punctuation

def check_text(string):
    if ('[id' in string and '|' in string and ']' in string):
        string = string.split(',', 1)[1]
    string = string.replace('\n', ' ')
    return string[1:]

def get_wordlist(texts: List[str]) -> List[str]:
    all_words = []
    for text in texts:
        for token in punctuation_tokens:
            if token in text:
                text = text.replace(token, '')

        words = text.split(' ')
        for word in words:
            if (word != ''):
                all_words.append(word)
    return all_words

def del_enters(string):
    string = string.replace('\n', ' ')
    string = string.replace(',', ';') # строки, содержащие запятые, разбиваются по ним и сохраняются в разных ячейках
    string = string.replace('  ', ' ')
    return string

def get_time(post):
    time = ((f"{datetime.fromtimestamp(post['date'])}").split(' '))[1]
    return time

def get_week(string):
    spliter = string.split('-')
    day = date(int(spliter[0]), int(spliter[1]), int(spliter[2]))
    return calendar.day_name[day.weekday()]

def transform(post: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    result['text'] = del_enters(post['text'])
    
    pictures = list(
        map(
            lambda x: x["photo"],
            filter(
                lambda x: x and x["type"] == "photo",
                post.get("attachments") or [],
            ),
        )
    )

    max_picture_link = ''
    max_size = 0
    
    for pic in pictures:
        for size in pic['sizes']:
            if (size['height'] * size['width'] > max_size):
                max_size = size['height'] * size['width']
                max_picture_link = size['url']

    result['link'] = max_picture_link
    result['comments'] = post['comments']['count']
    result['likes'] = post['likes']['count']
    result['reposts'] = post['reposts']['count']
    result['date'] = ((f"{datetime.fromtimestamp(post['date'])}").split(' '))[0]
    
    return result

vk_session = vk_api.VkApi(login, password)
vk_session.auth()

vk = vk_session.get_api()

comments_list = vk.wall.getComments(owner_id = OWNER_ID, post_id = POST_ID, need_likes = 0, offset = 0, count = 100, preview_length = 0)

comments_thread_list = []
comments_counter = 0
while (len(comments_thread_list) < 100 and comments_counter < comments_list['count']):
    comments_thread_list.append(comments_list['items'][comments_counter]['text'])
    thread_list = vk.wall.getComments(owner_id = OWNER_ID, post_id = POST_ID, need_likes = 0, offset = 0, count = 100, preview_length = 0, comment_id = comments_list['items'][comments_counter]['id'])
    thread_counter = 0
    while (len(comments_thread_list) < 100 and thread_counter < thread_list['count']):
        text = thread_list['items'][thread_counter]['text']
        comments_thread_list.append(check_text(text))
        thread_counter += 1
    comments_counter += 1

print("Totally got: {} comments".format(comments_list["count"]))
all_words = get_wordlist(comments_thread_list)
counter = Counter(all_words)
print(counter.most_common(20))

print('\nКоличество считанных комментариев:', len(comments_thread_list))
