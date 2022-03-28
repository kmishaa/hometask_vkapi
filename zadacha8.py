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

ID = -40886007
DOMAIN = 'https://vk.com/academicart'

FILE = 'result_of_zadacha5.csv'

punctuation_tokens = string.punctuation

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

posts_list = []
while (len(posts_list) < 300):
    counts = 300 - len(posts_list)
    if (counts > 100) :
        counts = 100
    posts = vk.wall.get(owner_id = ID, domain = DOMAIN, offset = len(posts_list), count = counts)
    posts_list += posts['items']

preprocessed_posts = map(transform, posts_list)

df = pd.DataFrame(preprocessed_posts)
df['time'] = list(map(get_time, posts_list))
df["day_week"] = list(map(get_week, df['date']))

print("Totally got: {} posts".format(posts["count"]))

all_words = get_wordlist(df['text'])
counter = Counter(all_words)
print(counter.most_common(20))

print('\nКоличество считанных постов:', len(posts_list))
