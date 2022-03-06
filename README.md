# CourseMCBotVK

VK Bot for my project https://coursemc.space

## Deploy locally:

> Install Python(If it's not installed)<br>
> [Download Python3](https://www.python.org/downloads/)

Clone the repository and go to installed folder:
```
git clone https://github.com/Ryize/CourseMCBotVK.git
cd CourseMCBotVK
```

Install requirements:
```
pip3 install -r requirements.txt
```

Specify your TOKEN and GROUP_ID:
```
server = Server(api_token=VK_T, group_id=207629753, url=URL, standart_head=STANDART_HEAD)
```

Run the bot:
```
python3 start.py
```

The bot is used as an alternative to the course website.

> Technologies used in the project: Python3, vk-api, threading, requests, json, re.
