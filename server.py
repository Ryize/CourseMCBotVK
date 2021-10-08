import re
from datetime import date

from utils import VkBot, KeyboardMixin, APIBackendMixin
from config import PAGE_1, PAGE_2


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
        schedules_with_html = self.post(PAGE_2+'get_by_username/', json=True, data={'username': username})
        schedules = self.remove_html(schedules_with_html, key_dict=key_dict, line_splitter=key_splitter, date_key_splitter=date_key_splitter)

        self.send_msg(send_id, message='Последние четыре расписания👇👇👇')
        self.send_msg(send_id, message=schedules, keyboard=self.get_standart_keyboard())
        self.send_msg(send_id, message='Сайт с полным расписанием: coursemc.space')

    def command_hide_keyboard(self, send_id: int):
        self.send_msg(send_id, message='Клавиатура скрыта!', keyboard=self.hide_keyboard())

    def command_return_keyboard(self, send_id: int):
        self.send_msg(send_id, message='✌️Вернул вам клавиатуру!', keyboard=self.get_standart_keyboard())

    def command_login(self, send_id: int):
        command = self._text_in_msg.replace(self._command_args+' ', '')
        login, password = command.split(', ')
        students_data = self.__api.get(PAGE_1, json=True)

        if self._LoginManager.authenticate(str(send_id), login):
            self.send_msg(send_id, message='✅Вы успешно авторизованны!', keyboard=self.get_standart_keyboard())
            return True

        for student_data in students_data:
            if student_data['name'] == login and student_data['password'] == password:
                self._LoginManager.new_user(send_id, login)
                print("!")
                self.send_msg(send_id, message='✅Вы успешно авторизованны!', keyboard=self.get_standart_keyboard())
                return True
        self.send_msg(send_id, message='❌Логин или пароль не верны!')
