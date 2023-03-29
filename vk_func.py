import json
from pprint import pprint

import vk_api
from vk_api.exceptions import ApiError
from config import user_token

TOKEN_VK_USER = user_token
# TOKEN_VK_GROUP = group_token

session = vk_api.VkApi(token=TOKEN_VK_USER)

# Ищет людей по критериям используем метод 'users.search'
# gender 1-ж  2-м
# age_from возраст от .. age_to возраст до
def search_users(gender, age, city):
    all_persons = []
    link = 'https://vk.com/id'
    vk_ = session
    response = vk_.method('users.search',
                          {'sort': 1,
                           'sex': gender,
                           'status': 1,
                           'age_from': int(age) - 2,
                           'age_to': int(age) + 2,
                           'has_photo': 1,
                           'count': 10,
                           'online': 1,
                           'hometown': city,
                           'fields': 'bdate'
                           })
    for element in response['items']:
        person = [
            element['first_name'],
            element['last_name'],
            link + str(element['id']),
            element['id'],
            element['bdate'],
            # фото_ссылка
            # element['bdate']
        ]
        all_persons.append(person)

    return all_persons

# Находим фото человека по его id
def get_photo(user_owner_id):
    vk_ = session
    attachments = {}
    try:
        response = vk_.method('photos.get',
                              {'access_token': TOKEN_VK_USER,
                                'v': '5.131',
                                'owner_id': user_owner_id,
                                'album_id': 'profile',
                                'count': 3,
                                'extended': 1,
                              })
        attachments['owner_id'] = response['items'][-2]['owner_id']
        attachments['photo_id'] = response['items'][-2]['id']
        attachments['url'] = response['items'][-2]['sizes'][-2]['url']
        # pprint(response['items'][-1])

        return attachments

    except ApiError:
        return 'в доступе к фото отказано'

# JSON файл
def json_file(list_):
    res = {}
    res_list = []
    for num, info in enumerate(list_):
        res['first_name'] = info[0]
        res['second_name'] = info[1]
        res['link'] = info[2]
        res['id'] = info[3]
        res['bdate'] = info[4]
        res_list.append(res.copy())

    with open("info.json", "a", encoding='UTF-8') as write_file:
        json.dump(res_list, write_file, ensure_ascii=False)

    print(f'json файл создан')

# list_ = search_users(1, 22, 'Черноголовка')
# print(list_)
# list_of = get_photo(275954747)
