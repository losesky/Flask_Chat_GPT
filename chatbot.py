import configparser
import logging
import os
import sqlite3
import uuid

import openai
from flask import Flask, render_template, request, jsonify
from flask import g

app = Flask(__name__, static_folder='static')

app.config['SESSION_COOKIE_TIMEOUT'] = 60

#  测试环境可以用，但生产环境这里异常，待排查
config = configparser.ConfigParser()
config.read('config.cfg')
openai.api_key = config.get('OpenAI', 'API_KEY')

prompt = ""

DATABASE_INIT_FILE = os.path.join("./", "schema.sql")
# LOG_FILE = os.path.join("./", "chatbot.log")
logging.basicConfig(filename='/var/log/chatbot.log', level=logging.INFO)


def connect_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect('chatbot.db')
    return db


def init_db():  # 使用数据库建模文件初始化数据库，在命令行中使用一次即可。
    print("初始化数据库，在命令行中使用一次即可".format(DATABASE_INIT_FILE))
    with app.app_context():
        db = connect_db()
        with app.open_resource(DATABASE_INIT_FILE, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def close_db(exception):
    if hasattr(g, 'db'):
        g.db.close()


def reset():
    global prompt
    prompt = ""


@app.route('/')
def index():
    # 第一次启动时初始化数据库
    init_db()
    return render_template('index.html')


@app.route('/prompt/<prompt_id>')
def get_prompt(prompt_id):
    try:
        conn = g.db
        cursor = conn.cursor()
        cursor.execute('SELECT prompt FROM prompts WHERE prompt_id = ?', (prompt_id,))
        row = cursor.fetchone()
        if row is None:
            return ''
        else:
            return row[0]
    except Exception as e:
        conn.rollback()
        print(e)
        raise TypeError("select error:{}".format(e))  # 抛出异常


@app.route('/prompts', methods=['GET'])
def get_prompts():
    try:
        conn = g.db
        cursor = conn.cursor()
        cursor.execute('SELECT prompt_id, prompt FROM prompts ORDER BY update_time DESC LIMIT 10')
        rows = cursor.fetchall()
        return jsonify(rows)
    except Exception as e:
        conn.rollback()
        print(e)
        raise TypeError("select error:{}".format(e))  # 抛出异常


def insert_prompt(response_prompt):
    prompt_id = str(uuid.uuid4())
    try:
        conn = g.db
        cursor = conn.cursor()
        cursor.execute("INSERT INTO prompts (prompt_id,prompt) VALUES (?,?)", (prompt_id, response_prompt))
        conn.commit()
        return prompt_id
    except Exception as e:
        conn.rollback()
        return None
        print(e)
        raise TypeError("insert error:{}".format(e))  # 抛出异常


def update_prompt(prompt_id, response_prompt):
    try:
        conn = g.db
        cursor = conn.cursor()
        cursor.execute('UPDATE prompts SET prompt = ? WHERE prompt_id = ?', (response_prompt, prompt_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
        raise TypeError("update error:{}".format(e))  # 抛出异常


def delete_prompt(prompt_id):
    try:
        conn = g.db
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prompts WHERE prompt_id = ?", prompt_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
        raise TypeError("delete error:{}".format(e))  # 抛出异常


@app.route('/get_response', methods=['POST'])
def get_response():
    global prompt
    try:
        user_input = request.form['user_input']
        prompt_id = request.form['prompt_id']
        if prompt_id != "":
            prompt = get_prompt(prompt_id)
        else:
            prompt = ""

        #  输入 reset 重置会话
        if user_input == "reset":
            delete_prompt(prompt_id)
            prompt = ""
            return '让我们重新开始'.format(prompt)
        #  chatGPT接收的上下文最大长度4097，如果提交的问题字串长度超过则报错
        #  因此这里需要对长度做处理，把每次提交的问题根据长度追加到上下文中
        #  max_length 是prompt的最大长度，其决定了上下文内容
        max_length = 512
        len_input = len(user_input)
        len_pos = max_length - len_input
        if len(prompt) > max_length > len(user_input):
            prompt = prompt[-len_pos:] + user_input + "\n"
        elif max_length < len(user_input):
            prompt = user_input + "\n"
        else:
            prompt = prompt + user_input + "\n"
        #  engine：生成引擎的名称，默认为 text-davinci-002。
        #  prompt：生成请求的提示文本。
        #  temperature：生成结果的随机性。取值范围为 0.0 到 1.0，默认为 0.5。
        #  max_tokens：生成结果的最大令牌数。
        #  top_p：取生成概率最高的令牌。默认为 1.0，即不限制生成概率。
        #  frequency_penalty：频率惩罚，用于降低生成频繁出现的词语。
        #  presence_penalty：存在惩罚，用于降低生成词语存在概率。
        #  best_of：生成最优结果的数量，默认为 1。
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2048,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response = response['choices'][0]['text']
        #  把问题和答案加入上下文中，便于AI根据上下文回答问题
        prompt += response
        if prompt_id != "" and prompt_id is not None:
            update_prompt(prompt_id, prompt)
        else:
            prompt_id = insert_prompt(prompt)
        # 将返回数据封装成JSON格式
        response = {
            'prompt_id': prompt_id,
            'prompt': response
        }
        return response
    except Exception as e:
        print(e)
        return "我开小差了，请再说一次"


if __name__ == '__main__':
    #  日志输出文件配置
    # logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    app.run(debug=True)
