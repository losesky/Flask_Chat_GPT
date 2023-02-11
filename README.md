# OpenAI ChatGTP 聊天机器人 (GPT-3)
在这个示例中，使用OpenAI的GPT-3实现类似ChatGPT的对话功能

1.使用以下命令在Ubuntu服务器上安装所需的依赖：
```
sudo apt-get update
sudo apt-get install apache2 libapache2-mod-wsgi-py3 python3-pip
```

2.克隆项目到服务器：使用 git 命令从 Github 中克隆你的 Flask 项目到服务器对应路径
```
cd /var/www/
sudo git clone https://github.com/losesky/Flask_Chat_GPT.git
cd Flask_Chat_GPT
```
3.在Ubuntu服务器上创建虚拟环境：
```
python3 -m venv myenv
source myenv/bin/activate
```
4.使用以下命令安装所需的python包：
```
pip install -r requirements.txt
```
5.如果想通过测试环境调试，执行如下代码，即可看到测试环境的结果
```
export FLASK_APP=chatbot.py
flask run --host=0.0.0.0
```
6.如果想部署生产环境

6.1.先创建 WSGI 文件
```
sudo nano /var/www/Flask_Chat_GPT/chatbot.wsgi
```
在该文件中，添加以下内容：
```
#!/usr/bin/python
import sys
sys.path.insert(0, '/var/www/Flask_Chat_GPT')
from Flask_Chat_GPT import chatbot as application
```
6.2.创建 Apache 配置文件：
```
sudo nano /etc/apache2/sites-available/Flask_Chat_GPT.conf
```
在该文件中，添加以下内容：
```
<VirtualHost *:80>
    ServerName your_domain_or_IP
    WSGIDaemonProcess chatbot python-path=/var/www/Flask_Chat_GPT
    WSGIProcessGroup chatbot
    WSGIScriptAlias / /var/www/Flask_Chat_GPT/chatbot.wsgi
    <Directory /var/www/Flask_Chat_GPT>
        Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
请确保将 your_domain_or_IP 替换为您的域名或 IP 地址

6.3.启用 Apache 配置：
```
sudo a2ensite Flask_Chat_GPT
sudo systemctl restart apache2

#查看服务器状态
sudo systemctl status apache2
#查看服务器后台输出
journalctl -u apache2.service -f
#查看服务器错误日志
sudo tail /var/log/apache2/error.log
```
这样，这个Flask 项目应该已经可以在生产环境中使用了。

演示: \
http://sg-ov.losesky.net

参考：\
https://platform.openai.com/account/api-keys
