import random
import string

import pyshorteners
import wikipedia
from datetime import date

from utils import VkBot, FileDB
from config import PAGE_1, PAGE_2, PAGE_3


class Server(VkBot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def command_ping(self, send_id: int) -> None:
        self.send_msg(send_id, message='Понг!')

    def command_schedule(self, send_id: int) -> None:
        key_splitter = '🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n\n👉 '
        key_dict = ('theme', 'weekday', 'lesson_materials')
        date_key_splitter = ('weekday')

        username = self.get_user_by_id(str(send_id))
        schedules_with_html = self.post(PAGE_2+'get_by_username/', json=True, data={'username': username[0][1]})
        schedules = self.__to_read_data(schedules_with_html, key_dict=key_dict, line_splitter=key_splitter, date_key_splitter=date_key_splitter, max_size=4)

        if not bool(schedules):
            self.send_msg(send_id, message='У вас нету расписания, возможно вы ещё не обучаетесь!')
            return None
        self.send_msg(send_id, message='Последние четыре расписания\n👇👇👇👇')
        self.send_msg(send_id, message=schedules, keyboard=self.get_standart_keyboard())
        self.send_msg(send_id, message='Сайт с полным расписанием:\nhttps://coursemc.space')

    def command_hide_keyboard(self, send_id: int):
        self.send_msg(send_id, message='Клавиатура скрыта!', keyboard=self.hide_keyboard())

    def command_return_keyboard(self, send_id: int):
        self.send_msg(send_id, message='✌️Вернул вам клавиатуру!', keyboard=self.get_standart_keyboard())

    def command_login(self, send_id: int):
        command = self._text_in_msg.replace(self._command_args+' ', '')
        try:
            login, password = command.split(', ')
        except ValueError:
            self.send_msg(send_id, message='⛔️Не верный формат входа!\nВводите данные в формате:\n/login Имя Пользователя, Пароль\n\n⚠️️Запятая обязательна!')
            return None
        students_data = self.get(PAGE_1, json=True)

        if self.authenticate(str(send_id), login):
            self.send_msg(send_id, message='⚠️Вы уже авторизованны!', keyboard=self.get_standart_keyboard())
            return True

        for student_data in students_data:
            if student_data['name'] == login and student_data['password'] == password:
                groups = student_data['groups']
                self.new_user(str(send_id), login, groups)
                self.send_admin_msg(f'👤Авторизован новый пользователь: {login}, из группы: {groups}')
                self.send_msg(send_id, message='✅Вы успешно авторизованны!', keyboard=self.get_standart_keyboard())
                return True
        self.send_msg(send_id, message='❌Логин или пароль не верны!')

    def command_notification(self, send_id: int):
        text_in_msg = self._text_in_msg.replace(self._command_args, '')
        users_groups = list(text_in_msg)[1]
        users = FileDB().get_by_value(value=users_groups, index=2)
        text = text_in_msg[2:]
        self.send_notification(text, send_id, users)


    def command_anotification(self, send_id: int):
        text = self._text_in_msg.replace(self._command_args, '')
        self.send_notification(text, send_id)

    def command_wiki(self, send_id: int):
        text_in_msg = self._text_in_msg.replace(self._command_args, '')
        wikipedia.set_lang("ru")
        try:
            text = f'{wikipedia.summary(text_in_msg)}\n\nПолная статья: {wikipedia.page(text_in_msg).url}'
        except:
            self.send_msg(send_id, message='😢 Вы ввели не известный запрос!')
            return
        self.send_msg(send_id, message=text)

    def command_generate_password(self, send_id):
        try:
            size = int(self._text_in_msg.replace(self._command_args, ''))
        except:
            size = 8
            self.send_msg(send_id, message='Длинна пароля не указанна или указанна неверно. Использованная длинна пароля - 8')

        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        text = ''.join(random.choice(chars) for x in range(size))
        self.send_msg(send_id, message=text)

    def command_short_url(self, send_id: int):
        text_in_msg = self._text_in_msg.replace(self._command_args, '')

        short_url = pyshorteners.Shortener().clckru.short(text_in_msg)
        if len(short_url) > 100:
            self.send_msg(send_id, message=f'🚧 Вы ввели не верную ссылку!')
            return
        self.send_msg(send_id, message=f'✈️Короткая ссылка: {short_url}')

    def command_groups(self, send_id: int):
        key_splitter = '------------------------------\n\n👉 '
        key_dict = ('id', 'title')
        groups = self.get(PAGE_3, json=True)
        text = self.__to_read_data(groups, key_dict, key_splitter)
        self.send_msg(send_id, message=f'👨‍🏫Все группы:\n\n👉{text}В настоящий момент это все группы!')


    def __to_read_data(self, entry_list: list, key_dict: tuple = (), line_splitter: str = '\n',
                    exclude_key_splitter: tuple = (), date_key_splitter: tuple = (), max_size: int = None) -> str:
        schedules_str = ''
        entry_list.reverse()
        if max_size:
            entry_list = entry_list[:-max_size]
        entry_list.reverse()
        for key, value in enumerate(entry_list):
            for i, j in enumerate(key_dict):
                if i + 1 == len(key_dict):
                    schedules_str += self.remove_html(value[j]) + '\n'
                elif j not in exclude_key_splitter and j not in date_key_splitter:
                    schedules_str += self.remove_html(str(value[j])) + '\n👉 '
                elif j in date_key_splitter:
                    str_fix = list(date.fromisoformat(value[j]).strftime("%A, %d. %B %Y"))
                    str_fix[0] = str_fix[0].upper()
                    schedules_str += ''.join(str_fix) + '\n👉 '
                else:
                    schedules_str += self.remove_html(value[j]) + ' '
            schedules_str += line_splitter
        return schedules_str