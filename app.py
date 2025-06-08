from flask import Flask, jsonify, send_from_directory, request
import os
import pandas as pd

app = Flask(__name__, static_folder='static')
DATA_DIR = 'data'

# 获取所有csv文件名
@app.route('/api/files')
def list_files():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    return jsonify({'files': files})

# 获取某个csv文件内容（转json）
@app.route('/api/data/<filename>')
def get_csv(filename):
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    try:
        df = pd.read_csv(file_path)
        return jsonify({'data': df.to_dict(orient='records')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 前端静态文件
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# 支持前端js/css等静态资源
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
