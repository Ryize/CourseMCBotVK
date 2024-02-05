import datetime
import random
import re
import string
import threading
import time

import pyshorteners
import requests
import wikipedia

from datetime import date

from vk_learn.core.utils import FileDB
from vk_learn.release import VkBot
from vk_learn.config import (PAGE_1, PAGE_2, PAGE_3, PAGE_4, PAGE_5,
                             PAGE_PAYMENT, PAGE_MISSING, PAGE_REVIEW_PROJECT)
from yookassa_worker import get_payment_url, check_payment


class Server(VkBot):
    """
    All the bot logic is the upper level of the system, inherited from the parents
    providing the necessary functionality and allowing you to focus only on writing business logic
    """

    def __init__(self, admins, *args, **kwargs):
        self._admins = admins
        self.__last_project_to_review_pk = 0
        super().__init__(*args, **kwargs)
        self.admins = self._admins
        self.follow_projects_for_review()

    def follow_projects_for_review(self):
        threading.Thread(target=self._follow_projects_for_review).start()

    def _follow_projects_for_review(self):
        while True:
            self.command_application(self.admins[0], time_=True)
            projects = self.get(PAGE_REVIEW_PROJECT, json=True)
            for i in projects['reviews']:
                if self.__last_project_to_review_pk >= i['id']:
                    continue
                text = f'❗️Пришёл проект на ревью!\nСсылка: {i["github"]}\nКомментарий: {i["comment"]}'
                self.send_admin_msg(text)
                self.__last_project_to_review_pk = i['id']
            time.sleep(120)

    def command_ping(self, send_id: int) -> None:
        self.send_msg(send_id, message='Понг!')

    def command_schedule(self, send_id: int) -> None:
        if send_id in self.admins:
            class_schedule = self.get(
                PAGE_4 + str(self.get_user_by_id(str(send_id))[0][1]) + '/',
                json=True)
            groups = self.get(PAGE_3, json=True)
            students = self.get(PAGE_1, json=True)
            dict_with_date = {
                'Понедельник': [],
                'Вторник': [],
                'Среда': [],
                'Четверг': [],
                'Пятница': [],
                'Суббота': [],
                'Воскресенье': [],
            }
            for key, schedule in enumerate(class_schedule):
                for group in groups:
                    if int(group['id']) == int(schedule['group']):
                        student_string = ''
                        for student in students:
                            if student['groups'] == int(group['id']):
                                student_string += '\nСтудент: {username}\n'.format(
                                    username=student['name'])
                        class_schedule[key]['group'] = group[
                                                           'title'] + student_string
                        time_ = class_schedule[key]['time_lesson']
                        class_schedule[key]['time_lesson'] = time_[:-3]
                        dict_with_date[class_schedule[key]['weekday']].append(
                            class_schedule[key])
                        break
            for day, weekday in dict_with_date.items():
                result_message = '{day}\n\n'.format(day=day)
                weekday.sort(key=lambda x: x['time_lesson'])
                for schedule in weekday:
                    result_message += '👉{time_lesson} ({duration}) ' \
                                      '{group_title}\n' \
                                      '{slasher}\n\n'.format(
                        time_lesson=schedule['time_lesson'],
                        duration=schedule['duration'][1:5],
                        group_title=schedule['group'],
                        slasher='🔥' * 12,
                    )
                self.send_msg(send_id, message=result_message)
            return

        key_splitter = '🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n\n👉 '
        key_dict = ('theme', 'weekday', 'lesson_materials')
        date_key_splitter = ('weekday',)

        username = self.get_user_by_id(str(send_id))
        schedules_with_html = self.post(PAGE_2 + 'get_by_username/', json=True,
                                        data={'username': username[0][1]})
        schedules = self.__to_read_data(schedules_with_html, key_dict=key_dict,
                                        line_splitter=key_splitter,
                                        date_key_splitter=date_key_splitter,
                                        max_size=4)

        if not bool(schedules):
            self.send_msg(send_id,
                          message='У вас нету расписания, возможно вы ещё не обучаетесь!')
            return
        self.send_msg(send_id, message='Последние четыре расписания\n👇👇👇👇')
        self.send_msg(send_id, message=schedules,
                      keyboard=self.get_standart_keyboard())
        self.send_msg(send_id,
                      message='Сайт с полным расписанием:\nhttps://coursemc.space')

    def command_hide_keyboard(self, send_id: int):
        self.send_msg(send_id, message='Клавиатура скрыта!',
                      keyboard=self.hide_keyboard())

    def command_return_keyboard(self, send_id: int):
        self.send_msg(send_id, message='✌️Вернул вам клавиатуру!',
                      keyboard=self.get_standart_keyboard())

    def command_login(self, send_id: int):
        command = self.get_command_text(self._text_in_msg, self._command_args)
        try:
            login, password = command.split(', ')
        except ValueError:
            self.send_msg(send_id,
                          message='⛔️Не верный формат входа!\nВводите данные в формате:\n/login Имя Пользователя, Пароль\n\n⚠️️Запятая обязательна!')
            return
        students_data = self.get(PAGE_1, json=True)

        if self.authenticate(str(send_id), login):
            self.send_msg(send_id, message='⚠️Вы уже авторизованны!',
                          keyboard=self.get_standart_keyboard())
            return

        for student_data in students_data:
            if student_data['name'] == login and student_data[
                'password'] == password:
                groups = student_data['groups']
                self.new_user(str(send_id), login, groups)
                self.send_admin_msg(
                    f'👤Авторизован новый пользователь: {login}, из группы: {groups}')
                self.send_msg(send_id, message='✅Вы успешно авторизованны!',
                              keyboard=self.get_standart_keyboard())
                return
        self.send_msg(send_id, message='❌Логин или пароль не верны!')

    def command_wiki(self, send_id: int):
        text_in_msg = self.get_command_text(self._text_in_msg,
                                            self._command_args)
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
            self.send_msg(send_id,
                          message='Длинна пароля не указанна или указанна неверно. Использованная длинна пароля - 8')

        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        text = ''.join(random.choice(chars) for x in range(size))
        self.send_msg(send_id, message=text)

    def command_short_url(self, send_id: int):
        text_in_msg = self.get_command_text(self._text_in_msg,
                                            self._command_args)

        short_url = pyshorteners.Shortener().clckru.short(text_in_msg)
        if len(short_url) > 100:
            self.send_msg(send_id, message=f'🚧 Вы ввели не верную ссылку!')
            return
        self.send_msg(send_id, message=f'✈️Короткая ссылка: {short_url}')

    def command_who_i(self, send_id: int):
        try:
            user, group = self._get_user_and_group(str(send_id))
            text = f"👤Информация о вас:\n\n👀 Вы авторизованны как: {user[0][1]}\n👨‍🎓 Вы обучаетесь в группе: {group['title']}\n📝 Ваш цифровой id: {user[0][0]}"
        except:
            text = f"❌ Ваш аккаунт не верно настроен, обратитесь к своему учителю!"
        self.send_msg(send_id, message=f'{text}')

    def command_get_users_data(self, send_id: int):
        data = FileDB().read()
        self.send_msg(send_id, message=f'🔒 Все данные:\n\n{data}')

    def command_helpop(self, send_id: int):
        text_in_msg = self.get_command_text(self._text_in_msg,
                                            self._command_args)
        if not text_in_msg:
            self.send_msg(send_id,
                          message=f'⛔️ Ваше обращение не может быть пустым!')
            return
        self.send_msg(send_id,
                      message=f'✅ Ваше обращение принято.\nАдминистрация рассмотрит его и ответит Вам в ближайшее время')
        user, group = self._get_user_and_group(str(send_id))
        self.send_admin_msg(
            f"👤 Пользователь {user[0][1]}, из группы: {group['title']}\nНаписал: {text_in_msg}\n\n📞Для ответа ему используйте такой id: {send_id}")

    # Command for Administators
    def command_groups(self, send_id: int):
        key_splitter = '------------------------------\n\n👉 '
        key_dict = ('id', 'title')
        groups = self.get(PAGE_3, json=True)
        text = self.__to_read_data(groups, key_dict, key_splitter)
        self.send_msg(send_id,
                      message=f'👨‍🏫Все группы:\n\n👉{text}В настоящий момент это все группы!')

    def command_notification(self, send_id: int):
        text_in_msg = self._text_in_msg.replace(self._command_args, '')
        users_groups = list(text_in_msg)[2]
        text_in_msg = self.get_command_text(self._text_in_msg,
                                            self._command_args)
        try:
            int(users_groups)
        except:
            self.send_msg(send_id, message='❌ Вы не указали номер группы!')
            return
        users = FileDB().get_by_value(value=users_groups, index=2)
        text = text_in_msg[2:]
        self.send_notification(text, send_id, users)
        self.send_msg(send_id,
                      message=f'✅ Сообщение в группу {int(users_groups)} успешно отправлено!')

    def command_anotification(self, send_id: int):
        text = self.get_command_text(self._text_in_msg, self._command_args)
        for user in FileDB().splitter():
            self.send_notification(text, send_id, user)
        self.send_msg(send_id, message='✅ Сообщение успешно отправлено!')

    def command_chat_with_mates(self, send_id: int):
        user, group = self._get_user_and_group(str(send_id))
        text_in_msg = self._text_in_msg.replace(self._command_args, '')
        users_groups = group['id']
        text_in_msg = self.get_command_text(self._text_in_msg,
                                            self._command_args)

        users = FileDB().get_by_value(value=str(users_groups), index=2)
        text = text_in_msg[2:]
        self.send_notification(text_in_msg, send_id, users,
                               f'Новое сообщение из чата [{user[0][1]}]:\n')
        self.send_msg(send_id, message='✅ Ваше сообщение успешно отправленно!')

    def command_translate(self, send_id: int):
        self.send_msg(send_id,
                      message='Для перевода вашего предложения, отправьте сообщение боту (не используя команду). Пример:\n\nWhat are you doing?\nЧто делаешь?')

    def command_application(self, send_id: int, time_: int = None):
        app_training = self.get(PAGE_5, json=True)
        result_app = ''
        for train in app_training:
            result_app += f'Имя: {train["name"]}\n' \
                          f'Способ связи: {train["contact"]}\n' \
                          f'Почта: {train["email"]}\n' \
                          f'Заявка создана: {train["created_at"][:10]}\n\n\n'
        if time_:
            if result_app:
                self.send_msg(send_id,
                              message=f'Необработанные заявки:\n{result_app}')
        else:
            self.send_msg(send_id,
                          message=f'Необработанные заявки:\n{result_app}')

    def command_payment(self, send_id: int):
        username = self.get_user_by_id(str(send_id))[0][1]
        amount = self.get(f'{PAGE_PAYMENT}{username}/', json=True).get(
            'amount')
        if not amount:
            self.send_msg(send_id, message=f'✅ Вы уже всё оплатили!')
            return
        url, payment_id = get_payment_url(amount)
        with open('payments.txt', 'a') as file:
            file.write(f'{send_id}/{payment_id}\n')
        self.send_msg(
            send_id,
            message=f'Счет на оплату сформирован.\n\nСумма: {amount}\nАдрес оплаты:\n{url}',
            keyboard=self.get_payment_keyboard()
        )

    def check_payment(self, event):
        send_id = event.object.peer_id
        username = self.get_user_by_id(str(send_id))[0][1]
        amount = self.get(f'{PAGE_PAYMENT}{username}/', json=True).get(
            'amount')
        with open('payments.txt') as file:
            text = file.read().split('\n')
        counter = 0
        for key, i in enumerate(text[::-1]):
            if counter == 7:
                continue
            payment_information = i.split('/')
            if payment_information[0] and int(
                    payment_information[0]) == send_id:
                counter += 1
                if check_payment(payment_information[1], amount):
                    self.success_payment(event)
                    del text[key]
                    with open('payments.txt', 'w') as file:
                        file.write('\n'.join(text))
                    self.post(f'{PAGE_PAYMENT}{username}/')
                    break
        else:
            self.canceled_payment(event)

    def skipping_a_class(self, send_id: int) -> None:
        self.send_msg(send_id, message='Вы точно хотите пропустить занятие?',
                      keyboard=self.skipping_a_class_keyboard())

    def skip(self, send_id: int) -> None:
        self.send_msg(send_id,
                      message='Выберите время отсутствия.\n'
                              'Либо введите кол-во пропускаемых уроков (число)\n',
                      keyboard=self.absence_schedule_keyboard())

    def absence_schedule(self, send_id: int) -> None:
        try:
            username = self.get_user_by_id(str(send_id))[0][1]
            current_date = datetime.date.today()
            tomorrow = current_date + datetime.timedelta(days=1)
            # Приведение даты к нужному формату
            tomorrow = tomorrow.strftime('%Y-%m-%d')
            skip = self.text_in_msg
            if skip.isdigit():
                total_passes = int(skip)
            if skip == 'Буду отсутствовать одно занятие':
                total_passes = 1
            elif skip == 'Буду отсутствовать два занятия':
                total_passes = 2
            elif skip == 'Буду отсутствовать три занятия':
                total_passes = 3
            elif skip == 'Буду отсутствовать четыре занятия':
                total_passes = 4
            elif skip == 'Буду отсутствовать пять занятий':
                total_passes = 5
            data = {
                'username': username,
                'date': tomorrow
            }
            for i in range(total_passes):
                self.post(PAGE_MISSING, data, json=True)
            self.send_msg(send_id,
                          message='Сообщение об отсутствии отправлено.',
                          keyboard=self.get_standart_keyboard())
            if total_passes == 1:
                declension = 'занятие'
            elif 1 < total_passes < 5:
                declension = 'занятия'
            else:
                declension = 'занятий'
            self.send_admin_msg(
                f'{username} пропускает {total_passes} {declension}')
        except requests.exceptions.RequestException as e:
            print('Произошла ошибка при выполнении запроса:', e)
            self.send_msg(send_id, message='Сообщение не отправлено. \n'
                                           'Повторите попытку.',
                          keyboard=self.get_standart_keyboard())

    def change_your_mind(self, send_id: int) -> None:
        self.send_msg(send_id, message='Отлично! Встретимся на занятие!',
                      keyboard=self.get_standart_keyboard())

    # Utility functions
    def _get_user_and_group(self, user_id: str):
        groups = self.get(PAGE_3, json=True)
        user = FileDB().get_by_value(value=user_id, index=0)
        for group in groups:
            if group['id'] == int(user[0][2]):
                return user, group

    def __to_read_data(self, entry_list: list, key_dict: tuple = (),
                       line_splitter: str = '\n',
                       exclude_key_splitter: tuple = (),
                       date_key_splitter: tuple = (),
                       max_size: int = None) -> str:
        schedules_str = ''
        entry_list.reverse()
        if max_size:
            entry_list = entry_list[:max_size]
        entry_list.reverse()
        for key, value in enumerate(entry_list):
            for i, j in enumerate(key_dict):
                if i + 1 == len(key_dict):
                    schedules_str += self.remove_html(value[j]) + '\n'
                elif j not in exclude_key_splitter and j not in date_key_splitter:
                    schedules_str += self.remove_html(str(value[j])) + '\n👉 '
                elif j in date_key_splitter:
                    str_fix = list(
                        date.fromisoformat(value[j]).strftime("%A, %d. %B %Y"))
                    str_fix[0] = str_fix[0].upper()
                    schedules_str += ''.join(str_fix) + '\n👉 '
                else:
                    schedules_str += self.remove_html(value[j]) + ' '
            schedules_str += line_splitter
        return schedules_str
