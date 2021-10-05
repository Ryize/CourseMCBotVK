from config import VK_API_TOKEN, URL, STANDART_HEAD

if __name__ == '__main__':
    from server import Server

    server = Server(api_token=VK_API_TOKEN, group_id=207629753, url=URL, standart_head=STANDART_HEAD, debug=True)

    COMMANDS = {
        '/help': {
            'command': server.command_help,
            'comment': 'Получить список всех комманд',
        },
        '/пинг': {
            'command': server.command_ping,
            'comment': 'Проверить работоспособность бота',
        },
        '✅Все расписания': {
            'command': server.command_schedule,
            'comment': 'Получить своё расписание',
        },
        '☠️Скрыть клавиатуру': {
            'command': server.command_hide_keyboard,
            'comment': 'Получить своё расписание',
        },
        '⛳️Вернуть клавиатуру': {
            'command': server.command_return_keyboard,
            'comment': 'Получить своё расписание',
        },
        '/login *args': {
            'command': server.command_login,
            'comment': 'Получить своё расписание',
        },
    }

    server.start(COMMANDS)