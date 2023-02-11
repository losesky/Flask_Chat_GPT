from flask import Flask, render_template, request
import openai
import configparser


app = Flask(__name__)
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
        prompt += user_input + "\n"

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
        prompt += response
        print(response)
        return response
    except Exception as e:
        print(e)
        return "ChatGPT开小差了，需要联系管理员: " + str(e)


if __name__ == '__main__':
    app.run()
