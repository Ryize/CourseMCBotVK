from vk_learn.config import VK_T, URL, STANDART_HEAD

GROUP_ID = 207629753
VK_ID_MATVEY_CHEKASHOV = 513239285
VK_ID_ALEXANDRA_TITARENKO = 655080669

if __name__ == '__main__':
    from server import Server

    server = Server(admins=(VK_ID_MATVEY_CHEKASHOV,),
                    api_token=VK_T, group_id=GROUP_ID, url=URL,
                    standart_head=STANDART_HEAD)

    COMMANDS = {
        '/help': {
            'command': server.command_help,
            'comment': 'Получить список всех команд',
        },
        'Начать *nshow': {
            'command': server.command_help,
            'comment': 'Получить список всех команд',
        },
        '💳 Оплата *nshow': {
            'command': server.command_payment,
            'comment': 'Оплатить занятия',
        },
        '🔎Помощь *nshow': {
            'command': server.command_help,
            'comment': 'Получить список всех команд',
        },
        '/я *auth': {
            'command': server.command_who_i,
            'comment': 'Получить информацию про свой аккаунт',
        },
        '/helpop *auth *args': {
            'command': server.command_helpop,
            'comment': 'Отправить вопрос или пожелания Администрации',
        },
        '⚾️Пинг *nshow': {
            'command': server.command_ping,
            'comment': 'Проверить работоспособность бота',
        },
        '✅Все расписания *auth *nshow': {
            'command': server.command_schedule,
            'comment': 'Получить своё расписание',
        },
        '✍️Заявки *admin *nshow': {
            'command': server.command_application,
            'comment': 'Получить заявки на обучение',
        },
        '/wiki *args': {
            'command': server.command_wiki,
            'comment': 'Поиск по википедии',
        },
        '/пароль *args': {
            'command': server.command_generate_password,
            'comment': 'Генерация случайного пароля. Пример: /пароль 16 (Второй аргумент это длинна пароля, по умолчания 8 символов)',
        },
        '/сократить *args': {
            'command': server.command_short_url,
            'comment': 'Сократить ссылку. Пример: /сократить https://google.com',
        },
        '☠️Скрыть клавиатуру *nshow': {
            'command': server.command_hide_keyboard,
            'comment': 'Получить своё расписание',
        },
        '📌️Вернуть клавиатуру *nshow': {
            'command': server.command_return_keyboard,
            'comment': 'Получить своё расписание',
        },
        '/login *args': {
            'command': server.command_login,
            'comment': 'Авторизация, формат: /login Матвей Чекашов, 1234 (Запятую между логином и паролем ставить '
                       'ОБЯЗАТЕЛЬНО!)',
        },
        '/translate': {
            'command': server.command_translate,
            'comment': 'Получить информацию по использованию переводчика',
        },
        '/группы *admin': {
            'command': server.command_groups,
            'comment': 'Список всех групп',
        },
        '/msg *admin': {
            'command': server.command_msg,
            'comment': 'Отправить пользователю сообщение через бота(По id)',
        },
        '/gnote *admin': {
            'command': server.command_notification,
            'comment': 'Отправить уведомление всем пользователям',
        },
        '/anote *admin': {
            'command': server.command_anotification,
            'comment': 'Отправить уведомление всем пользователям',
        },
        '/Получить данные *admin': {
            'command': server.command_get_users_data,
            'comment': 'Отправить уведомление всем пользователям',
        },
        '/killbot *admin': {
            'command': server.command_killbot,
            'comment': 'Остановить бота',
        },
        'Пропустить занятие *nshow *auth': {
            'command': server.skipping_a_class,
            'comment': 'Отправить уведомление на сайт о пропуске занятия',
        },
        'Пропустить *nshow *auth': {
            'command': server.skip,
            'comment': 'Подтверждение пропуска занятия',
        },
        'Я передумал *nshow *auth': {
            'command': server.change_your_mind,
            'comment': 'Отказ от пропуска занятия',
        },
        'Буду отсутствовать одно занятие *nshow *auth': {
            'command': server.absence_schedule,
            'comment': 'График отсутствия',
        },
        'Буду отсутствовать два занятия *nshow *auth': {
            'command': server.absence_schedule,
            'comment': 'График отсутствия',
        },
        'Буду отсутствовать три занятия *nshow *auth': {
            'command': server.absence_schedule,
            'comment': 'График отсутствия',
        },
        'Буду отсутствовать четыре занятия *nshow *auth': {
            'command': server.absence_schedule,
            'comment': 'График отсутствия',
        },
        'Буду отсутствовать пять занятий *nshow *auth': {
            'command': server.absence_schedule,
            'comment': 'График отсутствия',
        },
        '🏠 На главную *nshow': {
            'command': server.command_return_keyboard,
            'comment': 'Вернуть клавиатуру',
        },
    }
    while True:
        server.start(COMMANDS)
