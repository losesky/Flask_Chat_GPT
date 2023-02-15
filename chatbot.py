import logging

from flask import Flask, render_template, request
import openai
import configparser


app = Flask(__name__, static_folder='static')
# logging.basicConfig(filename='/var/log/chatbot.log', level=logging.INFO)
app.config['SESSION_COOKIE_TIMEOUT'] = 60

# 测试环境可以用，但生产环境这里异常，待排查
config = configparser.ConfigParser()
config.read('config.cfg')
openai.api_key = config.get('OpenAI', 'API_KEY')

prompt = ""


def reset():
    global prompt
    prompt = ""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    global prompt
    try:
        user_input = request.form['user_input']
        logging.info("user_input:\n"+user_input)
        prompt += user_input + "\n"
        # chatGPT接收的上下文最大长度4097，如果提交的问题字串长度超过则报错
        # 因此这里需要对长度做处理，把每次提交的问题根据长度追加到上下文中
        input_len = len(user_input) + 2
        if len(prompt) > 2048:
            prompt = prompt[-input_len:] + user_input + "\n"

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
            temperature=0.3,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response = response['choices'][0]['text']
        # 把问题和答案加入上下文中，便于AI根据上下文回答问题
        prompt += response
        logging.info("response:"+response)
        return response
    except Exception as e:
        logging.error(e)
        return "我开小差了，请再说一次"


if __name__ == '__main__':
    app.run(debug=False)
