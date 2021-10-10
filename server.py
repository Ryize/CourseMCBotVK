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
                self.new_user(str(send_id), login)
                self.send_admin_msg(f'👤Авторизован новый пользователь: {login}')
                self.send_msg(send_id, message='✅Вы успешно авторизованны!', keyboard=self.get_standart_keyboard())
                return True
        self.send_msg(send_id, message='❌Логин или пароль не верны!')

    def command_notification(self, send_id: int):
        text = self._text_in_msg.replace(self._command_args, '')
        self.send_notification(text, send_id)