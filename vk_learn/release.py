import sys

from vk_api.bot_longpoll import VkBotEventType
from vk_api.utils import get_random_id

from vk_learn.core.utils import BaseStarter, LoginManagerMixin, APIBackendMixin, KeyboardMixin, FileDB


class VkBot(BaseStarter, LoginManagerMixin, APIBackendMixin, KeyboardMixin):
    """
    A class that has collected all the basic elements for creating a fully functional bot
    (Launching, working with an account, working with an external API, working with a keyboard).
    Implemented basic commands needed in most bots
    """

    def __init__(self, *args, **kwargs):
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
        """ Получаем фамилию пользователя"""
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
                        message += f"{command_not_param}: {self.commands[command]['comment']}  😎\n\n"
                else:
                    message += command_not_param + ': ' + self.commands[command]['comment'] + '\n\n'
        self.send_msg(send_id, message=message, keyboard=self.get_standart_keyboard())

    def command_msg(self, send_id: int):
        text_in_msg = self._text_in_msg.replace(self._command_args, '')
        user_id = text_in_msg.split()[1]
        msg = ' '.join(text_in_msg.split()[2:])
        username = FileDB().get_by_value(value=user_id, index=0)
        username = username[0][1]
        if not self.__send_notification(send_id, msg, [user_id], system_name=f'[{username}]'):
            self.send_msg(send_id,
                          message=f'⛔️ Вы указали не верный id пользователя!',
                          )
            return
        self.send_msg(send_id,
                      message=f'✅️ Сообщение пользователю: {username} - успешно отправлено!',
                      )

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
            self.send_msg(send_id,
                          message=f'⛔️ Группы с таким номером нету!',
                          )
            return
    

    def __send_notification(self, send_id: int, text: str, user_data: list, system_name: str = None):
        if self.system_name == system_name or not system_name:
            system_name = self.system_name
        try:
            user_id = int(user_data[0])
        except:
            return
        if send_id == user_id:
            return False
        else:
            self.send_msg(user_id,
                          message=f'{system_name}: {text}\n{self.standart_msg_block}',
                          )
        return True

    def start(self, commands: dict, debug: bool = None) -> None:
        """ Запуск бота """
        print('Я запущен!')

        if (self.debug != debug) and (debug is not None):
            self.debug = debug

        self.commands = commands
        for event in self._long_poll.listen():  # Слушаем сервер
            # Пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:
                send_id = event.object.peer_id
                if self.debug:
                    if send_id in self.admins:
                        self._command_starter(event=event)
                else:
                    try:
                        self._command_starter(event=event)
                    except Exception as exc:
                        text_message = event.object.text
                        username = '\n👤Имя пользователя: {}\n📝Текст сообщения: {}'.format(self.get_full_name(send_id),
                                                                                            text_message)
                        self.__error_handler(exc=exc, any=username)
                        self.send_msg(send_id,
                                      message='🆘На сервере произошла ошибка🆘\nМы уже оповестили Администрацию об этом, приносим свои извинения💌',
                                      keyboard=self.get_standart_keyboard())
    def get_command_text(self, command, command_args):
        return''.join(list(command.replace(command_args, ''))[1:]).lstrip()

    def __error_handler(self, exc, any: str = ''):
        self.send_admin_msg(f'❌Произошла ошибка: {exc}\n{any}')
