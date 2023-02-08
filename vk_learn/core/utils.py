import requests
import json
import re
import vk_api.vk_api

from typing import Union
from googletrans import Translator
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotMessageEvent
from vk_api.utils import get_random_id

from vk_learn.core.exceptions import AuthError, CommandStopError


class FileDB:
    """
    Сlass that implements the basic logic of working with files, writing, reading, splitting into lists by element, etc.
    this class covers the need for basic file handling
    """

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
    """
    Logic of basic work with users, authorization, creating a new user, getting a user by id of VK.
    For work, another class is used FileDB
    """

    def __init__(self, file_name: str = 'test.txt', *args, **kwargs):
        self.__FileDB = FileDB(file_name)
        super().__init__(*args, **kwargs)

    def authenticate(self, id: str, login: str = None):
        id = str(id)
        user_data = self.__FileDB.get_by_value(id, index=0)
        if not login:
            return user_data
        if user_data:
            if user_data[0][1] == login:
                return True

    def new_user(self, id: str, login: str, groups: int):
        self.__FileDB.write(f'{id}/{login}/{groups}')

    def get_user_by_id(self, id: str):
        return self.__FileDB.get_by_value(value=id)


class APIBackendMixin:
    """
    The logic of working with the API, the logic of receiving data by get, post requests,
    and also converting them to json and back
    """

    def __init__(self, url: str = 'https://127.0.0.1', standart_head: str = '/api/', *args, **kwargs):
        self.url = url
        self.standart_head = standart_head
        self.full_url = url + standart_head
        super().__init__(*args, **kwargs)

    def get(self, page: str = '', json: bool = False, data: dict = None):
        if data:
            data = requests.get(self.full_url + page, verify=False, data=data).text
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
        return re.sub(r'\<[^>]*\>', '', value).replace('&nbsp;', ' ')


class KeyboardMixin(VkKeyboard):
    """
    Working with the VK keyboard, implemented methods for
    getting, hiding the keyboard and showing auxiliary commands
    """

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
    """
    The main class for the work of the VK bot.
    Implemented the logic for launching the bot,
    automatically catching errors, applying command parameters, etc.
    """

    def __init__(self, api_token, group_id, debug: bool = False, *args, **kwargs):

        # Для Long Poll
        self.__vk = vk_api.VkApi(token=api_token)

        # Для использования Long Poll API
        self._long_poll = VkBotLongPoll(self.__vk, group_id)

        # Для вызова методов vk_api
        self._vk_api = self.__vk.get_api()

        # Режим отладки(Когда он включёт ошибка будет останавливать программу
        self.debug = debug

        # Аргументы команлы
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
        self.chat_id = chat_id

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
                requested_function(chat_id)
                break

        else:
            translator = Translator()
            if translator.detect(text_in_msg).lang == 'ru':
                translation_text = translator.translate(text_in_msg, dest='en').text
            else:
                translation_text = translator.translate(text_in_msg, dest='ru').text
            self._vk_api.messages.send(peer_id=chat_id,
                                       message=translation_text,
                                       random_id=get_random_id(), )

    def __error_handler(self, exc):
        print(f'Произошла ошибка: {exc}!')

    def __get_args_command(self, command: str, text_in_msg: str) -> Union[bool, str]:
        command_args = command.split(' *')[1:]
        command = command.split(' *')[0]

        self._command_args = command

        return_data = []
        try:
            text_in_msg = text_in_msg.split('/')[1]
            command = command.replace('/', '')
        except:
            pass
        command_suffix = ('stop', 'nshow', 'auth', 'admin', 'args')
        for i in command_suffix:

            if text_in_msg.split(''.join(command))[0] == '':
                break
        else:
            return
        if text_in_msg.find(command) != -1 and command_args.count('stop'):
            self._command_args = command
            raise CommandStopError('Эта команда сейчас не работает!')

        if text_in_msg.find(command) != -1 and command_args.count('nshow') != 0:
            return_data.append(True)

        if text_in_msg.find(command) != -1 and command_args.count('auth') != 0:
            if not LoginManagerMixin().authenticate(str(self.__send_id)):
                raise AuthError('Вы не авторизованны!')
            return_data.append(True)

        if text_in_msg.find(command) != -1 and command_args.count('admin') != 0:
            if self.__send_id in self.admins:
                self._command_args = command
                return_data.append(command)

        if text_in_msg.find(command) != -1 and command_args.count('args'):
            self._command_args = command
            return_data.append(command)
        return return_data
