import vk_api

login = '' # логин при входе вк
password = '' # пароль

ID = -40886007
DOMAIN = 'https://vk.com/academicart'

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

print("Totally got: {} posts".format(posts["count"]))
print(posts_list[0])
print('\nКоличество считанных постов:', len(posts_list))
