#!/bin/bash

# 创建部署目录
echo "创建部署目录..."
mkdir -p trading-bot-backend
cp app.py paper_trading_bot.py run_paper_trading.py requirements.txt trading-bot-backend/

# 创建.env文件
echo "创建.env文件..."
cat > trading-bot-backend/.env << EOL
BINANCE_API_KEY=你的币安API密钥
BINANCE_API_SECRET=你的币安API密钥
OPENAI_API_KEY=你的OpenAI API密钥
EOL

# 创建supervisor配置
echo "创建supervisor配置..."
cat > trading-bot.conf << EOL
[program:trading-bot]
directory=/root/trading-bot-backend
command=python3 run_paper_trading.py
autostart=true
autorestart=true
stderr_logfile=/var/log/trading-bot.err.log
stdout_logfile=/var/log/trading-bot.out.log

[program:trading-api]
directory=/root/trading-bot-backend
command=gunicorn -w 4 -b 0.0.0.0:5000 app:app
autostart=true
autorestart=true
stderr_logfile=/var/log/trading-api.err.log
stdout_logfile=/var/log/trading-api.out.log
EOL

# 打包文件
echo "打包文件..."
tar czf deploy.tar.gz trading-bot-backend trading-bot.conf

# 使用scp上传文件
echo "上传文件到服务器..."
scp -o StrictHostKeyChecking=no deploy.tar.gz root@172.26.37.126:/root/

# 创建远程执行的脚本
echo "创建远程执行脚本..."
cat > remote_setup.sh << EOL
#!/bin/bash

# 解压文件
cd /root
tar xzf deploy.tar.gz

# 安装必要的软件
apt update
apt install -y python3 python3-pip supervisor

# 安装Python依赖
cd /root/trading-bot-backend
pip3 install -r requirements.txt

# 配置supervisor
mv /root/trading-bot.conf /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
supervisorctl start all

# 清理临时文件
rm /root/deploy.tar.gz
EOL

# 上传远程执行脚本
echo "上传远程执行脚本..."
scp -o StrictHostKeyChecking=no remote_setup.sh root@172.26.37.126:/root/

# 执行远程脚本
echo "执行远程设置..."
ssh -o StrictHostKeyChecking=no root@172.26.37.126 "chmod +x /root/remote_setup.sh && /root/remote_setup.sh"

# 清理本地临时文件
echo "清理本地临时文件..."
rm deploy.tar.gz remote_setup.sh
rm -rf trading-bot-backend trading-bot.conf

echo "部署完成！" 