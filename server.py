from utils import VkBot, KeyboardMixin, APIBackend
from config import PAGE_1, PAGE_2


class Server(VkBot, KeyboardMixin):

    def __init__(self, *args, **kwargs):
        self.__api = APIBackend(**kwargs)
        super().__init__(**kwargs)

    def command_help(self, send_id: int) -> None:
        message = ''
        for command in self.commands:
            message += command + ': ' + self.commands[command]['comment'] + '\n'
        self.send_msg(send_id, message=message)

    def command_ping(self, send_id: int) -> None:
        self.send_msg(send_id, message='Понг!')

    def command_schedule(self, send_id: int) -> None:
        schedule = self.__api.get(PAGE_2)

        self.send_msg(send_id, message=schedule, keyboard=self.get_standart_keyboard())

    def command_hide_keyboard(self, send_id: int):
        if not self._LoginManager.login_required(str(send_id)):
            self.send_msg(send_id, message='Вы не авторизованны!', keyboard=self.hide_keyboard())
            return False
        self.send_msg(send_id, message='Клавиатура скрыта!', keyboard=self.hide_keyboard())

    def command_return_keyboard(self, send_id: int):
        if not self._LoginManager.login_required(str(send_id)):
            self.send_msg(send_id, message='Вы не авторизованны!', keyboard=self.hide_keyboard())
            return False
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
