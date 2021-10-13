import locale
import sys
from datetime import date
from typing import Union

import requests
import json
import re
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotEventType
import vk_api.vk_api

from vk_api.bot_longpoll import VkBotLongPoll, VkBotMessageEvent
from vk_api.utils import get_random_id

from exceptions import AuthError, CommandStopError


class FileDB:
    def __init__(self, file_name: str = 'test.txt', *args, **kwargs):
        self.__file_name = file_name
        super().__init__(*args, **kwargs)

    def write(self, data: str):
        with self.__file_open('a') as file:
            file.write(data + '\n')

    def read(self):
        with self.__file_open('r') as file:
            return file.read()

    def readlines(self):
        with self.__file_open('r') as file:
            return file.read().split('\n')

    def splitter(self, splitter: str = '/'):
        data_list = self.readlines()
        return_values = []
        for string in data_list:
            return_values.append(string.split(splitter))
        return return_values

    def get_by_index(self, index: int = 0, splitter: str = '/'):
        return_values = []
        for i in self.splitter(splitter):
            return_values.append(i[index])
        return return_values

    def get_by_value(self, value: str = '0', splitter: str = '/', index: int = None):
        return_values = []
        try:
            for i in self.splitter(splitter):
                if index:
                    if value == i[index]:
                        return_values.append(i)
                else:
                    for j in i:
                        if value == j:
                            return_values.append(i)
        except:
            pass
        return return_values

    def __file_open(self, code: str):
        return open(self.__file_name, code)

    @property
    def file_name(self):
        return self.file_name

    @file_name.setter
    def file_name(self, file_name):
        self.file_name = file_name


class LoginManagerMixin:
    def __init__(self, file_name: str = 'test.txt', *args, **kwargs):
        self.__FileDB = FileDB(file_name)
        super().__init__(*args, **kwargs)

    def authenticate(self, id: str, login: str = None):
        id = str(id)
        user_data = self.__FileDB.get_by_value(id, index=0)
        if not login:
            return user_data
        if user_data:
            if user_data[1] == login:
                return True

    def new_user(self, id: str, login: str, groups: int):
        self.__FileDB.write(f'{id}/{login}/{groups}')

    def get_user_by_id(self, id: str):
        return self.__FileDB.get_by_value(value=id)


class APIBackendMixin:
    def __init__(self, url: str = 'https://127.0.0.1', standart_head: str = '/api/', *args, **kwargs):
        self.url = url
        self.standart_head = standart_head
        self.full_url = url + standart_head
        super().__init__(*args, **kwargs)

    def get(self, page: str = '', json: bool = False):
        data = requests.get(self.full_url + page, verify=False).text
        if json:
            data = self.__to_json(data)
        return data

    def post(self, page: str = '', data: dict = '', json: bool = False):
        data = requests.post(self.full_url + page, data=data, verify=False).text
        if json:
            data = self.__to_json(data)
        return data

    def __to_json(self, data):
        return json.loads(data)

    @staticmethod
    def remove_html(value):
        return re.sub(r'\<[^>]*\>', '', value)

class KeyboardMixin(VkKeyboard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def hide_keyboard(self, label: str = '📌️Вернуть клавиатуру'):
        keyboard = VkKeyboard()
        keyboard.add_button(label=label, color=VkKeyboardColor.POSITIVE)
        return keyboard

    def get_standart_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_button(label='✅Все расписания', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button(label='🔎Помощь', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(label='⚾️Пинг', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(label='☠️Скрыть клавиатуру', color=VkKeyboardColor.NEGATIVE)
        return keyboard

    def get_help(self):
        keyboard = VkKeyboard()
        keyboard.add_button(label='🔎Помощь', color=VkKeyboardColor.POSITIVE)
        return keyboard


class BaseStarter:
    def __init__(self, api_token, group_id, debug: bool = False, *args, **kwargs):

        # Для Long Poll
        self.__vk = vk_api.VkApi(token=api_token)

        # Для использования Long Poll API
        self._long_poll = VkBotLongPoll(self.__vk, group_id)

        # Для вызова методов vk_api
        self._vk_api = self.__vk.get_api()

        # Режим отладки(Когда он включёт ошибка будет останавливать программу
        self.debug = debug

        # Команда с аргументами
        self._command_args = ''

        # Текст сообщения
        self._text_in_msg = ''

        # Список администраторов
        self.admins = []

        super().__init__(*args, **kwargs)

    def start(self, commands: dict) -> None:
        """ Запуск бота """

        self.commands = commands
        for event in self._long_poll.listen():  # Слушаем сервер

            # Пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.__command_starter(event=event)

    def _command_starter(self, event: VkBotMessageEvent) -> None:
        chat_id = event.object.peer_id
        text_in_msg = event.object.text

        self._text_in_msg = text_in_msg
        self.__send_id = chat_id

        for command in self.commands:
            try:
                param = self.__get_args_command(command, text_in_msg)
            except AuthError:
                self._vk_api.messages.send(peer_id=chat_id,
                                           message='🤫Вы не авторизованны! /help',
                                           random_id=get_random_id(),
                                           keyboard=KeyboardMixin().get_help().get_keyboard())
            except CommandStopError:
                self._vk_api.messages.send(peer_id=chat_id,
                                           message='👮Данная команда сейчас не доступна! /help',
                                           random_id=get_random_id(),
                                           keyboard=KeyboardMixin().get_help().get_keyboard())
            if (command.lower() == text_in_msg.lower()) or param:
                self.command = command
                requested_function = self.commands[command]['command']
                if self.debug:
                    requested_function(chat_id)
                else:
                    requested_function(chat_id)

    def __error_handler(self, exc):
        print(f'Произошла ошибка: {exc}!')

    def __get_args_command(self, command, text_in_msg) -> Union[bool, str]:
        command_args = command.split(' *')[1:]
        command = command.split(' *')[0]

        if text_in_msg.find(command) != -1 and command_args.count('stop'):
            self._command_args = command
            raise CommandStopError('Эта команда сейчас не работает!')

        elif text_in_msg.find(command) != -1 and command_args.count('nshow') != 0:
            return command

        elif text_in_msg.find(command) != -1 and command_args.count('auth') != 0:
            if not LoginManagerMixin().authenticate(str(self.__send_id)):
                raise AuthError('Вы не авторизованны!')
            return True

        elif text_in_msg.find(command) != -1 and command_args.count('admin') != 0:
            if self.__send_id in self.admins:
                self._command_args = command
                return command


        elif text_in_msg.find(command) != -1 and command_args.count('args'):
            self._command_args = command
            return command


class VkBot(BaseStarter, LoginManagerMixin, APIBackendMixin, KeyboardMixin):

    def __init__(self, *args, **kwargs):
        #locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # the ru locale is installed
        self.system_name = '[Автоматическое оповещение]'
        self.standart_msg_block = ''
        super().__init__(*args, **kwargs)

    def send_msg(self, send_id: int, message: str, keyboard=None) -> None:
        """ Отправка сообщения """
        if keyboard:
            self._vk_api.messages.send(peer_id=send_id,
                                       message=message,
                                       random_id=get_random_id(),
                                       keyboard=keyboard.get_keyboard())
        else:
            self._vk_api.messages.send(peer_id=send_id,
                                       message=message,
                                       random_id=get_random_id())

    def get_user_name(self, user_id: int) -> str:
        """ Получаем имя пользователя"""
        return self._vk_api.users.get(user_id=user_id)[0]['first_name']

    def get_user_last_name(self, user_id: int) -> str:
        """ Получаем имя пользователя"""
        return self._vk_api.users.get(user_id=user_id)[0]['last_name']

    def get_full_name(self, send_id: int) -> str:
        return '{} {}'.format(self.get_user_name(send_id), self.get_user_last_name(send_id))

    def get_user_id(self, user_id: int) -> int:
        """ Получаем id пользователя"""
        return self._vk_api.users.get(user_id=user_id)[0]['id']

    def send_admin_msg(self, msg):
        for admin in self.admins:
            self.send_msg(admin, message=msg)

    def command_help(self, send_id: int) -> None:
        message = ''
        for command in self.commands:
            command_not_param = command.split(' *')[0]
            if not command.count('*nshow'):
                if command.count('*admin'):
                    if send_id in self.admins:
                        message += f"{command_not_param}: {self.commands[command]['comment']}😎\n\n"
                else:
                    message += command_not_param + ': ' + self.commands[command]['comment'] + '\n\n'
        self.send_msg(send_id, message=message, keyboard=self.get_standart_keyboard())

    def command_killbot(self, send_id: int):
        if send_id in self.admins:
            login = self.authenticate(str(send_id))[1]
            self.send_admin_msg(f'😈Бот успешно остановлен, Администратором {login}!')
            sys.exit()

    def send_notification(self, text: str, send_id: int, users: list = []) -> None:
        if not bool(text):
            text = '😅Тестовое сообщение!'
        if users:
            for user in users:
                if isinstance(users[0], list) == 1:
                    self.__send_notification(send_id, text, user)
                else:
                    self.__send_notification(send_id, text, users)
                    break
        else:
            for user in FileDB().splitter():
                self.__send_notification(send_id, text, user)
        self.send_msg(send_id,
                      message=f'👉Ваше сообщение:\n{text}\n\n👉С припиской:\n{self.standart_msg_block}\n\n✅Успешно отправленно!',
                      )

    def __send_notification(self, send_id: int, text: str, user_data: list):
        try:
            user_id = int(user_data[0])
        except:
            return None
        if send_id == user_id:
            pass
        else:
            self.send_msg(user_id,
                          message=f'{self.system_name}: {text}\n{self.standart_msg_block}',
                          )

    def start(self, commands: dict, debug: bool = None) -> None:
        """ Запуск бота """
        print('Я запущен!')

        if (self.debug != debug) and (debug is not None):
            self.debug = debug

        self.commands = commands
        for event in self._long_poll.listen():  # Слушаем сервер

            # Пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:
                if self.debug:
                    self._command_starter(event=event)
                else:
                    try:
                        self._command_starter(event=event)
                    except Exception as exc:
                        send_id = event.object.peer_id
                        text_message = event.object.text
                        username = '\n👤Имя пользователя: {}\n📝Текст сообщения: {}'.format(self.get_full_name(send_id),
                                                                                            text_message)
                        self.__error_handler(exc=exc, any=username)
                        self.send_msg(send_id,
                                      message='🆘На сервере произошла ошибка🆘\nМы уже оповестили Администрацию об этом, приносим свои извинения💌',
                                      keyboard=self.get_standart_keyboard())

    def __error_handler(self, exc, any: str = ''):
        self.send_admin_msg(f'❌Произошла ошибка: {exc}\n{any}')