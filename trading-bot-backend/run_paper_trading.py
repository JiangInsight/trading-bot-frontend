"""
Multi-Model Paper Trading Bot 使用示例
使用真实的Binance市场数据进行模拟交易，比较不同模型的实时表现
持续运行直到手动停止
"""

from paper_trading_bot import TradingBot
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import threading
import signal
import sys

# 全局变量，用于控制程序是否继续运行
running = True

def signal_handler(sig, frame):
    """处理Ctrl+C信号，安全停止程序"""
    global running
    print("\n\nReceived stop signal. Gracefully shutting down...")
    running = False
    print("Please wait for the current cycle to complete...")

def main():
    # 注册信号处理器，捕获Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # 你的API密钥
    binance_api_key = '0da245d7262f7e149eb8887eadfe26e2400a9f941b0e9a6532813b199338810f'
    binance_api_secret = '617d5b6018377895c1bf051b6911662ff9ca5efa9f41c5ad62a08c5bc5e9f2ca'
    openai_api_key = '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'
    
    # 交易参数
    symbol = 'BTCUSDT'
    initial_usdt = 300000.0
    interval = 10  # 每个周期之间的间隔（秒）
    
    # 创建四个不同模型的交易机器人
    bots = [
        TradingBot(binance_api_key, binance_api_secret, openai_api_key, 
                  model_name="gpt-4o-mini", symbol=symbol, initial_usdt=initial_usdt, bot_name="gpt4o_mini"),
        TradingBot(binance_api_key, binance_api_secret, openai_api_key, 
                  model_name="gpt-4.1-mini", symbol=symbol, initial_usdt=initial_usdt, bot_name="gpt4.1_mini"),
        TradingBot(binance_api_key, binance_api_secret, openai_api_key, 
                  model_name="gpt-4.1-nano", symbol=symbol, initial_usdt=initial_usdt, bot_name="gpt4.1_nano"),
        TradingBot(binance_api_key, binance_api_secret, openai_api_key, 
                  model_name="gpt-4.1", symbol=symbol, initial_usdt=initial_usdt, bot_name="gpt4.1")
    ]
    
    # 运行交易机器人
    print(f"Starting multi-model trading with {interval} second intervals")
    print("Press Ctrl+C to stop the program")
    
    cycle = 1
    global running
    
    while running:
        start_time = time.time()  # 记录周期开始时间
        
        print(f"\n--- Cycle {cycle} ---")
        
        try:
            # 创建线程列表，让所有模型同时做决策
            threads = []
            for bot in bots:
                thread = threading.Thread(target=bot.run_trading_cycle)
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            # 每个周期结束后显示当前状态
            print_current_status(bots)
            
            # 定期保存比较结果（每10个周期）
            if cycle % 10 == 0:
                save_comparison_results(bots, cycle)
            
            # 计算实际等待时间（考虑到执行时间）
            elapsed = time.time() - start_time
            wait_time = max(0, interval - elapsed)
            
            # 等待下一个周期
            if running:
                print(f"Waiting {wait_time:.1f} seconds for next cycle...")
                time.sleep(wait_time)
            
            cycle += 1
            
        except Exception as e:
            print(f"Error in cycle {cycle}: {e}")
            time.sleep(5)  # 发生错误时短暂暂停后继续
    
    # 程序结束时，保存最终结果
    print("\nTrading stopped. Saving final results...")
    compare_results(bots)
    print("Done!")

def print_current_status(bots):
    """打印所有模型的当前状态"""
    print("\n--- Current Status ---")
    status_data = []
    
    for bot in bots:
        account_info = bot.client.get_account_info(bot.symbol)
        status_data.append({
            'Model': bot.model_name,
            'USDT': f"{account_info.usdt_holding:.2f}",
            'Crypto': f"{account_info.holding:.8f}",
            'Total': f"{account_info.account_total:.2f}",
            'P/L': f"{account_info.account_total - 300000.0:.2f}",
            'Return %': f"{(account_info.account_total / 300000.0 - 1) * 100:.2f}%"
        })
    
    # 创建状态表格
    status_df = pd.DataFrame(status_data)
    print(status_df.to_string(index=False))

def save_comparison_results(bots, cycle):
    """定期保存比较结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 收集每个机器人的当前账户状态
    results = []
    for bot in bots:
        account_info = bot.client.get_account_info(bot.symbol)
        results.append({
            'Model': bot.model_name,
            'USDT Balance': account_info.usdt_holding,
            'Crypto Holding': account_info.holding,
            'Total Value': account_info.account_total,
            'Profit/Loss': account_info.account_total - 300000.0,
            'Return %': (account_info.account_total / 300000.0 - 1) * 100,
            'Cycle': cycle
        })
    
    # 保存比较结果到CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(f'model_comparison_cycle_{cycle}_{timestamp}.csv', index=False)
    
    # 绘制账户价值对比图
    plot_account_history(bots, cycle)

def compare_results(bots):
    """比较不同模型的交易结果"""
    print("\n=== Final Trading Results Comparison ===")
    
    # 收集每个机器人的最终账户状态
    results = []
    for bot in bots:
        account_info = bot.client.get_account_info(bot.symbol)
        results.append({
            'Model': bot.model_name,
            'USDT Balance': account_info.usdt_holding,
            'Crypto Holding': account_info.holding,
            'Total Value': account_info.account_total,
            'Profit/Loss': account_info.account_total - 300000.0,
            'Return %': (account_info.account_total / 300000.0 - 1) * 100
        })
    
    # 创建比较表格
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    # 保存比较结果到CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_df.to_csv(f'total_performance.csv', index=False)
    
    # 绘制账户价值对比图
    plot_account_history(bots)

def plot_account_history(bots, cycle=None):
    """绘制不同模型的账户价值历史对比图"""
    plt.figure(figsize=(12, 8))
    
    for bot in bots:
        # 读取账户历史数据
        try:
            df = pd.read_csv(bot.account_history_file)
            plt.plot(df['total_value'], label=f"{bot.model_name}")
        except Exception as e:
            print(f"Error plotting data for {bot.model_name}: {e}")
    
    title = 'Account Value Comparison'
    if cycle:
        title += f' (Cycle {cycle})'
    
    plt.title(title)
    plt.xlabel('Trading Cycles')
    plt.ylabel('Account Value (USDT)')
    plt.legend()
    plt.grid(True)
    
    # 保存图表
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'account_comparison_{timestamp}.png'
    if cycle:
        filename = f'account_comparison_cycle_{cycle}_{timestamp}.png'
    
    plt.savefig(filename)
    plt.close()
    
    print(f"Comparison chart saved as {filename}")

if __name__ == "__main__":
    main()
