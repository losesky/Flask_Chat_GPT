from flask import Flask, render_template, request
import openai
import configparser

app = Flask(__name__)

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

    return response


if __name__ == '__main__':
    app.run()
