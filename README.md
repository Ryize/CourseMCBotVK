# CourseMCBotVK

ВК бота проекта https://coursemc.ru

## Deploy locally:

> Установите Python (Если ещё не установлен)<br>
> [Download Python3](https://www.python.org/downloads/)

Клонируйте репозиторий и перейдите в установленную папку:
```
git clone https://github.com/Ryize/CourseMCBotVK.git
cd CourseMCBotVK
```

Установите requirements:
```
pip3 install -r requirements.txt
```

Укажите свой ТОКЕН и GROUP_ID:
```
server = Server(api_token=VK_T, group_id=207629753, url=URL, standart_head=STANDART_HEAD)
```

Запустите бота:
```
python3 start.py
```

Бот используется в качестве альтернативы веб-сайту курса (coursemc).

> Помогал в разработке: [Владимир Ездаков](https://github.com/Vivat67)

> Технологии, использованные в проекте: Python3, vk-api, threading, requests, json, re.
