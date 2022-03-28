import vk_api
from datetime import datetime
from typing import Dict, Any
import pandas as pd

login = '' # логин при входе вк
password = '' # пароль

ID = -40886007
DOMAIN = 'https://vk.com/academicart'

FILE = 'result_of_zadacha4.csv'

def del_enters(string):
    string = string.replace('\n', ' ')
    string = string.replace(',', ';') # строки, содержащие запятые, разбиваются по ним и сохраняются в разных ячейках
    string = string.replace('  ', ' ')
    return string

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

print("Totally got: {} posts".format(posts["count"]))

pd.set_option('display.max_columns', None)

df.to_csv(FILE)

print('\nКоличество считанных постов:', len(posts_list))
