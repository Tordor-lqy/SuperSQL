import requests
import json
import pymysql


def chatWithGPT(messages , requests):
    url = 'http://ai.tordor.top:47435/v1/chat/completions'

    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": messages
    })

    APIKEY = 'sk-qfpOPbQaCwy7Zv4m142aD48662374dEc88E92911Fc7fF46a'

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {APIKEY}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)


messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "Hello!"
    }
]


# print(chatWithGPT(messages))


def create_message(user_message):
    return [
        {
            "role": "user",
            "content": f"{user_message}"
        }
    ]


config = {
    'host': 'localhost',
    'port': 3306,
    'database': 'small_red_flower',
    'user': 'small_red_flower',
    'password': 'Pxsk3xd47hmpAHf5'
}


class DB:
    def __init__(self, config):
        self.conn = pymysql.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        self.conn.select_db(config["database"])

    def save_chat(self, meet_id, ai_name, ai_message):
        print("INSERT INTO ai_chat "
              "(meet_id, ai_name, ai_message)"
              f"VALUES ({meet_id}, {ai_name}, {ai_message})")
        self.cursor.execute(
            "INSERT INTO ai_chat "
            "(meet_id, ai_name, ai_message)"
            f"VALUES ({meet_id}, '{ai_name}', '{ai_message}')"
        )
        self.conn.commit()

    def save_meet(self, ai_meet_theme, ai_meet_round):
        print("INSERT INTO ai_meet "
              "(ai_meet_theme, ai_meet_round)"
              f"VALUES ({ai_meet_theme}, {ai_meet_round})")
        self.cursor.execute(
            "INSERT INTO ai_meet "
            "(ai_meet_theme, ai_meet_round)"
            f"VALUES ({ai_meet_theme}, {ai_meet_round})"
        )
        self.conn.commit()


class role:
    def __init__(self, name, prompt):
        self.prompt = prompt
        self.name = name
        self.messages = [
            {
                "role": "system",
                "content": f"{prompt} 你的所有回答请模仿人的语气 ， 回答只使用一段话不超过100字"
            }
        ]

    def add_content(self, content):
        self.messages.append({
            "role": f"user",
            "content": f"\n{content}"
        })

    def chat(self, chatWithGPT , requests):
        response = chatWithGPT(self.messages , requests)
        self.messages.append(response["choices"][0]["message"])
        return response["choices"][0]["message"]['content']


meet_id = 2
theme = "西红柿炒鸡蛋的创新与传统结合"
round = 3
roles = [
    {
        "name": "主持人",
        "prompt": "你是主持人，也是核心人物请站在大局思考问题,并且要提出疑问，抛出问题"
    },
    {
        "name": "技术专家",
        "prompt": "你是一个技术专家，从技术角度思考可行性，并且提出合理的建议"
    },
    {
        "name": "质疑者",
        "prompt": "你是一个批判者，善于在讨论中，找出关键点并且提出质疑"
    }
]


# roles = []

def run(DB, role, roles, theme, round, chatWithGPT , requests,meet_id):
    aidb = DB({
        'host': 'localhost',
        'port': 3306,
        'database': 'innov_ai',
        'user': 'innov_ai',
        'password': 'JM6h25e65wKF2JHd'
    })
    ais = []
    for i in roles:
        ais.append(role(i['name'], i['prompt']))
    chat_text = f"你现在正在参加一场会议会议主题是{theme},请站在你的角度"
    for i in range(int(round)):
        for a in ais:
            a.add_content(chat_text)
            response = a.chat(chatWithGPT , requests)
            print(response)
            aidb.save_chat(meet_id, a.name, response)
            chat_text += f'\n{a.name}:{response}\n'

import threading

t1 = threading.Thread(target=run, args=(DB, role, roles, theme, round, chatWithGPT , requests,meet_id))

t1.start()
