from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
from paper_trading_bot import PaperTradingClient, TradingBot
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# 开发阶段允许所有源访问
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 允许所有源访问
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

DATA_DIR = 'data'

def get_csv_files():
    if not os.path.exists(DATA_DIR):
        return []
    return [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')  # 从当前目录提供index.html

@app.route('/api/files')
def get_files():
    files = get_csv_files()
    return jsonify({"files": files})

@app.route('/api/data')
def get_data():
    csv_files = get_csv_files()
    data = []
    
    for csv_file in csv_files:
        file_path = os.path.join(DATA_DIR, csv_file)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if not df.empty:
                last_row = df.iloc[-1]
                data.append({
                    'bot_name': csv_file.replace('.csv', ''),
                    'timestamp': last_row.get('timestamp', ''),
                    'action': last_row.get('action', ''),
                    'price': last_row.get('price', 0),
                    'quantity': last_row.get('quantity', 0),
                    'value': last_row.get('value', 0)
                })
    
    return jsonify(data)

@app.route('/api/history/<bot_name>')
def get_history(bot_name):
    account_file = os.path.join(DATA_DIR, f'{bot_name}_account_history.csv')
    trade_file = os.path.join(DATA_DIR, f'{bot_name}_trade_history.csv')
    
    response = {'account': [], 'trade': []}
    
    if os.path.exists(account_file):
        df = pd.read_csv(account_file)
        response['account'] = df.to_dict('records')
        
    if os.path.exists(trade_file):
        df = pd.read_csv(trade_file)
        response['trade'] = df.to_dict('records')
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
