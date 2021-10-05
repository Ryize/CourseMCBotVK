import requests
import json
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotEventType
import vk_api.vk_api

from vk_api.bot_longpoll import VkBotLongPoll, VkBotMessageEvent
from vk_api.utils import get_random_id


class FileDB:
    def __init__(self, file_name: str = 'test.txt'):
        self.__file_name = file_name

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
        for i in self.splitter(splitter):
            if index:
                if value == i[index]:
                    return i
            else:
                for j in i:
                    if value == j:
                        return i

    def __file_open(self, code: str):
        return open(self.__file_name, code)

    @property
    def file_name(self):
        return self.file_name

    @file_name.setter
    def file_name(self, file_name):
        self.file_name = file_name


class LoginManager:
    def __init__(self, file_name: str = 'test.txt'):
        self.__FileDB = FileDB(file_name)

    def authenticate(self, id: str, login: str):
        id = str(id)
        user_data = self.__FileDB.get_by_value(id, index=0)
        if user_data:
            if user_data[1] == login:
                return True

    def new_user(self, id: str, login: str):
        self.__FileDB.write(f'{id}/{login}')

    def login_required(self, send_id):
        return self.__FileDB.get_by_value(send_id, index=0)


class APIBackend:
    def __init__(self, url: str = 'https://127.0.0.1', standart_head: str = '/api/', *args, **kwargs):
        self.url = url
        self.standart_head = standart_head
        self.full_url = url + standart_head

    def get(self, page: str = '', json: bool = False):
        data = requests.get(self.full_url + page, verify=False).text
        if json:
            data = self.__to_json(data)
        return data

    def __to_json(self, data):
        return json.loads(data)


class KeyboardMixin(VkKeyboard):
    def hide_keyboard(self, label: str = '⛳️Вернуть клавиатуру'):
        keyboard = VkKeyboard()
        keyboard.add_button(label=label, color=VkKeyboardColor.POSITIVE)
        return keyboard

    def get_standart_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_button(label='✅Все расписания', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(label='☠️Скрыть клавиатуру', color=VkKeyboardColor.NEGATIVE)
        return keyboard


class BaseStarter:
    def __init__(self, api_token, group_id, debug: bool = False, *args, **kwargs):

        # Для Long Poll
        self.__vk = vk_api.VkApi(token=api_token)

        # Для использования Long Poll API
        self.__long_poll = VkBotLongPoll(self.__vk, group_id)

        # Для вызова методов vk_api
        self._vk_api = self.__vk.get_api()

        # Режим отладки(Когда он включёт ошибка будет останавливать программу
        self.debug = debug

        # Команда с аргументами
        self._command_args = ''

        # Текст сообщения
        self._text_in_msg = ''

    def start(self, commands: dict, debug: bool = None) -> None:
        """ Запуск бота """
        print('Я запущен!')

        if (self.debug != debug) and (debug is not None):
            self.debug = debug

        self.commands = commands
        for event in self.__long_poll.listen():  # Слушаем сервер

            # Пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.__command_starter(event=event)

    def __command_starter(self, event: VkBotMessageEvent) -> None:
        chat_id = event.object.peer_id
        text_in_msg = event.object.text

        for command in self.commands:
            if (command.lower() == text_in_msg.lower()) or (self.__get_args_command(command, text_in_msg)):
                self.command = command
                requested_function = self.commands[command]['command']
                self._text_in_msg = text_in_msg
                if self.debug:
                    requested_function(chat_id)
                else:
                    try:
                        requested_function(chat_id)
                    except Exception as exc:
                        print('Произошла ошибка!\nДетали:', exc)

    def __get_args_command(self, command, text_in_msg):
        command_args = command.split(' *args')[0]
        if text_in_msg.find(command_args) != -1:
            self._command_args = command_args
            return command_args


class VkBot(BaseStarter):

    def __init__(self, *args, **kwargs):
        self._LoginManager = LoginManager()
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

    def get_user_id(self, user_id: int) -> int:
        """ Получаем id пользователя"""
        return self._vk_api.users.get(user_id=user_id)[0]['id']