from dataclasses import dataclass
from pprint import pprint

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from vk_func import search_users, get_photo
from db_vk import register_user, add_user, check_db_reg, check_db_user, list_favorite, delete_db_elit
from config import group_token, user_group_id

group_id = user_group_id

vk_session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_session)

# n = 0

@dataclass
class MsgBot:
    misunderstand = 'не понимаю о чём вы..'
    start = f'привет! \nесли хочешь начать поиск второй половинки:' \
            f'\n  -  задай критерии поиска ' \
            f'\nесли хочешь посмотреть ранее занесенное в избранное:' \
            f'\n  -  нажми "ИЗБРАННОЕ"'
    criterions = 'выберите критерии поиска'
    again = 'начнём сначала?'
    minage = 'введите минимальный возраст'
    maxage = 'введите максимальный возраст'
    sex = 'выберите пол'
    greetings = ['привет', 'приветик', 'хай', 'hello', 'start']
    leav = ['пока', 'конец', 'не хочу больше искать', 'goodbye']
    gd = 'пока!'
    city = 'введите название города'
    city_error = 'такого города нет'
    boy = 'выбраны мальчики'
    girl = 'выбраны девочки'

class VkBot():

    def send_msg(user_id, message, keyboard=None):
        params = {'user_id': user_id,
                  'message': message,
                  'random_id': randrange(10**5)}

        if keyboard != None:
            params['keyboard'] = keyboard.get_keyboard()

        vk_session.method('messages.send', params)

    print("server started")

    def set_keyboard_start(self):
        keyboard = VkKeyboard()
        keyboard.add_button('ЗАДАТЬ КРИТЕРИИ ПОИСКА', VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('ИЗБРАННОЕ', VkKeyboardColor.PRIMARY)
        return keyboard

    def set_search_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_button('ГОРОД', VkKeyboardColor.PRIMARY)
        keyboard.add_button('ПОЛ', VkKeyboardColor.PRIMARY)
        keyboard.add_button('ВОЗРАСТ', VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('ПОИСК', VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('НАЗАД', VkKeyboardColor.PRIMARY)
        return keyboard

    def sex_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_button('ОН', VkKeyboardColor.PRIMARY)
        keyboard.add_button('ОНА', VkKeyboardColor.PRIMARY)
        return keyboard

    def set_found_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_button('NEXT', VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('ДОБАВИТЬ В ИЗБРАННОЕ', VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('НА ГЛАВНУЮ', VkKeyboardColor.PRIMARY)
        return keyboard

    def set_favorite_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_button('NEXT', VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('УДАЛИТЬ', VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('НА ГЛАВНУЮ', VkKeyboardColor.PRIMARY)
        return keyboard


    def get_city_id(self, user_id):
        VkBot.send_msg(user_id, MsgBot.city, self.set_search_keyboard())

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                city = event.text
                return city

    def get_sex(self, user_id):
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()

                if text == 'он':
                    return 2

                elif text == 'она':
                    return 1

    def get_age(self, user_id):
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()

                if text.isdigit() and int(text) >= 14 and int(text) <= 200:
                    # VkBot.send_msg(user_id, f'Возраст {text} лет')
                    return int(text)

                else:
                    VkBot.send_msg(user_id, f'вы неправильно ввели параметры')
                    self.starting()

    def found(self, user_id, hometown, sex, age):

        n = 0

        list_of_users = search_users(sex, age, hometown)

        pprint(list_of_users)

        if len(list_of_users) != 0:

            print(n)

            photo_ = get_photo(list_of_users[n][3])

            if photo_ != 'в доступе к фото отказано':

                VkBot.send_msg(user_id, f'{list_of_users[n][0]} {list_of_users[n][1]} \n {list_of_users[n][2]}')

                photo = "photo{}_{}".format(photo_['owner_id'],
                                            photo_['photo_id'])
                vk_session.method("messages.send", {'peer_id': user_id, 'attachment': photo, "random_id": randrange(10**5)})

            elif photo_ == 'в доступе к фото отказано':

                VkBot.send_msg(user_id, f'{list_of_users[n][0]} {list_of_users[n][1]} \n {list_of_users[n][2]} '
                                        f'\n"закрытый профиль или нет фото"')

            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    text = event.text.lower()
                    user_vk_id = event.user_id

                    if text == 'добавить в избранное':

                        if check_db_user(list_of_users[n][3]) is None and photo_ != 'в доступе к фото отказано':

                            id_ = check_db_reg(user_vk_id).id
                            add_user(vk_id=list_of_users[n][3],
                                     name=list_of_users[n][0],
                                     surname=list_of_users[n][1],
                                     gender=sex,
                                     year=age,
                                     city=hometown,
                                     link=list_of_users[n][2],
                                     photo=photo_['url'],
                                     id_user=id_)

                            if check_db_user(list_of_users[n][3]) is not None:
                                VkBot.send_msg(user_id, f'{list_of_users[n][0]} {list_of_users[n][1]} добавлен(а) в избранное')

                        elif photo_ == 'в доступе к фото отказано':
                            VkBot.send_msg(user_id, f'добавить в избранное нельзя, т.к. нет фото или закрытый профиль')

                        elif check_db_user(list_of_users[n][3]) is not None:
                            VkBot.send_msg(user_id, f'{list_of_users[n][0]} {list_of_users[n][1]} уже есть в избранном')

                    elif text == 'next':

                        if n == len(list_of_users) - 1:

                            VkBot.send_msg(user_id, f'по данным параметрам больше никого нет!')

                        else:

                            n += 1

                            photo_ = get_photo(list_of_users[n][3])

                            if photo_ != 'в доступе к фото отказано':

                                VkBot.send_msg(user_id,
                                               f'{list_of_users[n][0]} {list_of_users[n][1]} \n {list_of_users[n][2]}')

                                photo = "photo{}_{}".format(photo_['owner_id'],
                                                            photo_['photo_id'])
                                vk_session.method("messages.send", {'peer_id': user_id, 'attachment': photo,
                                                                    "random_id": randrange(10 ** 5)})

                            elif photo_ == 'в доступе к фото отказано':

                                VkBot.send_msg(user_id,
                                               f'{list_of_users[n][0]} {list_of_users[n][1]} \n {list_of_users[n][2]} '
                                               f'\n"закрытый профиль или нет фото"')

                    elif text == 'на главную':
                        VkBot.send_msg(user_id, 'задать новые параметры или выбрать избранное?', self.set_keyboard_start())
                        self.starting()

        else:
            VkBot.send_msg(user_id, f'поиск не дал результата, введите новые параметры', self.set_keyboard_start())


    def set_search_params(self, user_id):
        dict_ = {}

        dict_2 = {'hometown': 'не выбран', 'sex': 'не выбран', 'age': 'не выбран'}

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()

                if text == 'город':
                    dict_['hometown'] = self.get_city_id(user_id)
                    dict_2['hometown'] = dict_.get("hometown")
                    VkBot.send_msg(user_id, f'город: {dict_2.get("hometown")}\nпол: {dict_2.get("sex")}\nвозраст: {dict_2.get("age")}', self.set_search_keyboard())

                elif text == 'пол':
                    VkBot.send_msg(user_id, 'он или она', self.set_search_keyboard())
                    dict_['sex'] = self.get_sex(user_id)

                    if dict_.get("sex") == 1:
                        dict_2['sex'] = 'она'
                    else:
                        dict_2['sex'] = 'он'

                    VkBot.send_msg(user_id, f'город: {dict_2.get("hometown")}\nпол: {dict_2.get("sex")}\nвозраст: {dict_2.get("age")}', self.set_search_keyboard())

                elif text == 'возраст':
                    VkBot.send_msg(user_id, 'введите возраст от 14 до 100', self.set_search_keyboard())
                    dict_['age'] = self.get_age(user_id)
                    dict_2['age'] = dict_.get("age")

                    VkBot.send_msg(user_id, f'город: {dict_2.get("hometown")}\nпол: {dict_2.get("sex")}\nвозраст: {dict_2.get("age")}', self.set_search_keyboard())

                elif text == 'поиск':
                    VkBot.send_msg(user_id, 'будем искать по вашим параметрам', self.set_found_keyboard())
                    self.found(user_id, dict_.get('hometown'), dict_.get('sex'), dict_.get('age'))

                elif text == 'назад' or text == 'Назад':
                    VkBot.send_msg(user_id, 'задать новые параметры или выбрать избранное?', self.set_keyboard_start())
                    self.starting()

    def favorite(self, user_id):

        list_users = list_favorite()

        y = 0
        i = list_users[y]
        photo_ = get_photo(i.get('vk_id'))
        VkBot.send_msg(user_id, f"""{i.get('name')} {i.get('surname')}\n{i.get('link')}""")
        photo = "photo{}_{}".format(photo_['owner_id'],
                                    photo_['photo_id'])
        vk_session.method("messages.send", {'peer_id': user_id, 'attachment': photo,
                                            "random_id": randrange(10 ** 5)})

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()
                user_vk_id = event.user_id

                if text == 'удалить':
                    delete_db_elit(i.get('vk_id'))
                    VkBot.send_msg(user_id, f"""Вы удалили {i.get('name')} {i.get('surname')}""")

                elif text == 'next':
                    y += 1
                    if y <= len(list_users) - 1:
                        i = list_users[y]
                        photo_ = get_photo(i.get('vk_id'))
                        VkBot.send_msg(user_id, f"""{i.get('name')} {i.get('surname')}\n{i.get('link')}""")
                        photo = "photo{}_{}".format(photo_['owner_id'],
                                                    photo_['photo_id'])
                        vk_session.method("messages.send", {'peer_id': user_id, 'attachment': photo,
                                                            "random_id": randrange(10 ** 5)})
                    else:
                        VkBot.send_msg(user_id, f'это все!"')

                elif text == 'на главную':
                    VkBot.send_msg(user_id, 'задать новые параметры или выбрать избранное?', self.set_keyboard_start())
                    self.starting()


    ##!!! ОСНОВНАЯ ФУНКЦИЯ
    def starting(self):
        # global n

        for event in longpoll.listen():

            if event.type == VkEventType.MESSAGE_NEW and event.to_me:

                text = event.text.lower()
                user_id = event.user_id

                if check_db_reg(user_id) is None:
                    register_user(user_id)
                else:
                    print('Ok')

                if text in MsgBot.greetings:
                    VkBot.send_msg(user_id, MsgBot.start, self.set_keyboard_start())

                elif text == 'задать критерии поиска':
                    VkBot.send_msg(user_id, 'введите параметры для вашей второй половинки', self.set_search_keyboard())
                    self.set_search_params(user_id)

                elif text == 'избранное':
                    VkBot.send_msg(user_id,'ваш список:', self.set_favorite_keyboard())
                    self.favorite(user_id)

                elif text == MsgBot.leav:
                    VkBot.send_msg(user_id, MsgBot.gd, self.set_keyboard_start())

                else:
                    VkBot.send_msg(user_id, MsgBot.misunderstand, self.set_keyboard_start())

bot = VkBot()
bot.starting()


