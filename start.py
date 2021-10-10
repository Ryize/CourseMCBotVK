from config import VK_API_TOKEN, URL, STANDART_HEAD

if __name__ == '__main__':
    from server import Server

    server = Server(api_token=VK_API_TOKEN, group_id=207629753, url=URL, standart_head=STANDART_HEAD, debug=True)

    server.admins = [513239285]

    COMMANDS = {
        '/killbot *admin': {
            'command': server.command_killbot,
            'comment': 'Остановить бота',
        },
        '/all *admin': {
            'command': server.command_notification,
            'comment': 'Отправить уведомление всем пользователям',
        },
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
        '⚾️Пинг': {
            'command': server.command_ping,
            'comment': 'Проверить работоспособность бота',
        },
        '✅Все расписания *auth': {
            'command': server.command_schedule,
            'comment': 'Получить своё расписание',
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
    }
    while True:
        server.start(COMMANDS)
