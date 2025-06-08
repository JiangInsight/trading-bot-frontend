# Paper Trading Bot

这是一个基于Python的加密货币纸面交易机器人，使用Binance API获取实时市场数据，并使用OpenAI的GPT模型进行交易决策。

## 功能特点

- 实时获取Binance市场数据
- 使用GPT模型进行市场分析和交易决策
- 模拟交易执行，包含手续费计算
- 完整的交易记录和账户状态跟踪
- Web界面监控（通过Flask实现）

## 安装要求

- Python 3.8+
- 依赖包列表见 `requirements.txt`

## 安装步骤

1. 克隆仓库：
```bash
git clone [你的仓库URL]
cd [仓库名]
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并添加以下配置：
```
BINANCE_API_KEY=你的币安API密钥
BINANCE_API_SECRET=你的币安API密钥
OPENAI_API_KEY=你的OpenAI API密钥
```

## 使用方法

1. 运行交易机器人：
```bash
python run_paper_trading.py
```

2. 运行Web监控界面：
```bash
python app.py
```

## 文件说明

- `paper_trading_bot.py`: 主要的交易机器人逻辑
- `run_paper_trading.py`: 运行交易机器人的脚本
- `app.py`: Web监控界面
- `static/`: Web界面静态文件
- `data/`: 交易数据存储目录

## 注意事项

- 这是一个纸面交易系统，不会执行实际的交易操作
- 请确保API密钥的安全性
- 建议先用小额进行测试

## License

MIT 