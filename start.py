from vk_learn.config import VK_T, URL, STANDART_HEAD

if __name__ == '__main__':
    from server import Server

    server = Server(api_token=VK_T, group_id=207629753, url=URL, standart_head=STANDART_HEAD, debug=False)

    server.admins = [513239285]

    COMMANDS = {
        '/help': {
            'command': server.command_help,
            'comment': 'Получить список всех команд',
        },
        'Начать *nshow': {
            'command': server.command_help,
            'comment': 'Получить список всех команд',
        },
        '🔎Помощь *nshow': {
            'command': server.command_help,
            'comment': 'Получить список всех команд',
        },
        '/я *auth': {
            'command': server.command_who_i,
            'comment': 'Получить информацию про свой аккаунт',
        },
        '⚾️Пинг': {
            'command': server.command_ping,
            'comment': 'Проверить работоспособность бота',
        },
        '✅Все расписания *auth': {
            'command': server.command_schedule,
            'comment': 'Получить своё расписание',
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
        '/группы *admin': {
            'command': server.command_groups,
            'comment': 'Список всех групп',
        },
        '/note *admin': {
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
    }
    while True:
        server.start(COMMANDS)
