# OpenAI ChatGTP 聊天机器人 (GPT-3)
在这个示例中，使用flask-gunicorn-nginx架构部署一个OpenAI的GPT-3类似的ChatGPT的会话小程序

1.使用以下命令在Ubuntu服务器上安装所需的依赖
```
$ sudo apt-get update
$ sudo apt-get install python3 python3-pip python3-virtualenv
```
然后安装 nginx
```
$ sudo apt-get install nginx
```
2.克隆项目到服务器/var/www \
使用 git 命令从 Github 中克隆你的 Flask 项目到服务器对应路径
```
$ cd /var/www/
$ sudo git clone https://github.com/losesky/Flask_Chat_GPT.git
$ sudo chmod 777 /var/www/Flask_Chat_GPT
$ cd Flask_Chat_GPT
```
3.在Ubuntu服务器上创建虚拟环境
```
$ sudo python3 -m venv myenv
$ sudo source myenv/bin/activate
```
4.在虚拟环境中使用以下命令安装所需的python项目依赖包
```
(venv) $ sudo pip install -r requirements.txt
```
5.如果想通过测试环境调试，执行如下代码，即可看到测试环境的结果
```
(venv) $ sudo export FLASK_APP=chatbot.py
(venv) $ sudo flask run --host=0.0.0.0
```
6.如果想部署生产环境

6.1.在虚拟环境中安装 Gunicorn
```
(venv) $ sudo pip install gunicorn
```
6.2.在虚拟环境中运行 Gunicorn
```
(venv) $ sudo gunicorn -w 4 -b 127.0.0.1:5001 --access-logfile access.log --error-logfile error.log chatbot:app
```
这时进程已经在运行，单独开一个终端，输入
```
$ sudo curl 127.0.0.1:5001
```
如果输出正常，则Gunicorn部署完成

6.3.进行Nginx 的配置，建议先备份一下 default 文件
```
$ sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
$ sudo nano /etc/nginx/sites-available/default
```
暴力修改成为以下的内容
```
server {
    listen 80;
    server_name sg-ov.losesky.net; # 这是HOST机器的外部域名，用地址也行

    location / {
        proxy_pass http://127.0.0.1:5001; # 这里是指向 gunicorn host 的服务地址
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

}
```
修改完成后，重新起动 nginx 服务
```
$ sudo service nginx restart
```
6.4.将 Gunicorn作为服务运行，我们在此将采用Systemd配置Flask程序在后台运行\
6.4.1.创建 Systemd 服务文件
```
$ sudo nano /etc/systemd/system/chatbot.service
```
6.4.2.将以下内容添加到文件中
```
[Unit]
Description=The chatbot service
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/Flask_Chat_GPT/
Environment=PATH=/var/www/Flask_Chat_GPT/myenv/bin
ExecStart=/var/www/Flask_Chat_GPT/myenv/bin/gunicorn --timeout 60 -w 4 -b 127.0.0.1:5001 --access-logfile access.log --error-logfile error.log chatbot:app
Restart=always

[Install]
WantedBy=multi-user.target
```
这里之所以设置-timeout 60 是因为Gunicorn默认超时是30秒，nginx默认超时是60秒，需要统一，不然会出现501错误

6.4.3.保存文件并退出编辑器\
6.4.4.加载服务配置
```
$ sudo systemctl daemon-reload
```
6.4.5.启动chatbot服务
```
$ sudo systemctl start chatbot
```
你可以通过一下命令管理服务
```
$ sudo systemctl status chatbot
$ sudo systemctl restart chatbot
$ sudo systemctl stop chatbot
$ sudo journalctl -u chatbot.service -f
# 查看错误日志
$ sudo tail -f /var/www/Flask_Chat_GPT/error.log
```
至此，基于Flask-gunicorn-nginx的chatGPT项目就部署完成，\
在云平台防火墙设置中开放:80 :5000 ：5001端口即可在外网访问了。

演示: \
http://sg-ov.losesky.net

备注：\
你需要在openai官网申请api-keys\
https://platform.openai.com/account/api-keys \
申请后，把api-key替换config.cfg文件中的”sk-********“即可。

参考：\
https://www.bmabk.com/index.php/post/31016.html \
https://www.cnblogs.com/Ray-liang/p/4837850.html



