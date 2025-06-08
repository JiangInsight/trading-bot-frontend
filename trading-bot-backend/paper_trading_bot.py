import time
import numpy as np
import os
import logging
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Union, Optional, Any
from dataclasses import dataclass
from enum import Enum
from binance.client import Client
from binance.exceptions import BinanceAPIException
from openai import OpenAI

# 设置日志级别
logging.getLogger().setLevel(logging.ERROR)

@dataclass
class MarketData:
    """Market data structure"""
    timestamp: float
    symbol: str
    price: float
    price_change: float
    price_change_percent: float
    weighted_avg_price: float
    prev_close_price: float
    last_price: float
    last_qty: float
    bid_price: float
    bid_qty: float
    ask_price: float
    ask_qty: float
    open_price: float
    high_price: float
    low_price: float
    volume: float
    quote_volume: float
    open_time: int
    close_time: int
    best_bid: float
    best_ask: float

@dataclass
class AccountInfo:
    """Account information structure"""
    holding: float
    usdt_holding: float
    account_total: float

@dataclass
class OrderResult:
    """Order execution result"""
    order_id: Optional[int] = None
    status: Optional[str] = None
    executed_qty: Optional[float] = None
    cummulative_quote_qty: Optional[float] = None
    error: Optional[str] = None

class PaperTradingClient:
    """Paper trading client with real market data from Binance"""
    
    def __init__(self, api_key: str, api_secret: str, initial_usdt: float = 300000.0):
        """Initialize paper trading client"""
        try:
            # 只用于获取市场数据，不进行实际交易
            self.client = Client(api_key, api_secret, testnet=False)  # 使用主网获取真实数据
            self.BinanceAPIException = BinanceAPIException
        except Exception as e:
            print(f"Binance client initialization failed: {e}")
            raise
        
        # 模拟账户状态
        self.usdt_holding = initial_usdt
        self.holding = 0.0  # 初始持仓为0
        self.fee_rate = 0.001  # 千分之一手续费
        self.order_id = 0
        
        print(f"Paper trading account initialized with {initial_usdt:,.2f} USDT")
    
    def get_market_data(self, symbol: str) -> Tuple[List[float], List[str]]:
        """Get real market data from Binance"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            stats = self.client.get_ticker(symbol=symbol)
            depth = self.client.get_order_book(symbol=symbol)
            
            data = MarketData(
                timestamp=time.time(),
                symbol=stats['symbol'],
                price=price,
                price_change=float(stats['priceChange']),
                price_change_percent=float(stats['priceChangePercent']),
                weighted_avg_price=float(stats['weightedAvgPrice']),
                prev_close_price=float(stats['prevClosePrice']),
                last_price=float(stats['lastPrice']),
                last_qty=float(stats['lastQty']),
                bid_price=float(stats['bidPrice']),
                bid_qty=float(stats['bidQty']),
                ask_price=float(stats['askPrice']),
                ask_qty=float(stats['askQty']),
                open_price=float(stats['openPrice']),
                high_price=float(stats['highPrice']),
                low_price=float(stats['lowPrice']),
                volume=float(stats['volume']),
                quote_volume=float(stats['quoteVolume']),
                open_time=stats['openTime'],
                close_time=stats['closeTime'],
                best_bid=float(depth['bids'][0][0]),
                best_ask=float(depth['asks'][0][0])
            )
            
            indicator_name = [
                'price', 'price_change', 'price_change_percent', 'weighted_avg_price',
                'bid_price', 'bid_qty', 'ask_price', 'ask_qty', 'volume',
                'open_price', 'high_price', 'low_price', 'close_price',
                'best_bid', 'best_ask'
            ]
            
            indicator = [
                data.price, data.price_change, data.price_change_percent, data.weighted_avg_price,
                data.bid_price, data.bid_qty, data.ask_price, data.ask_qty, data.volume,
                data.open_price, data.high_price, data.low_price, data.price,
                data.best_bid, data.best_ask
            ]
            
            return indicator, indicator_name
            
        except self.BinanceAPIException as e:
            print(f"Error getting market data: {e}")
            raise
    
    def execute_trade(self, quantity: float, symbol: str, side: str) -> OrderResult:
        """Execute simulated trade with fee calculation"""
        if quantity <= 0:
            return OrderResult(error="Trade quantity must be greater than 0")
        
        try:
            # 获取当前市场价格
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            self.order_id += 1
            
            if side.upper() == 'BUY':
                # 买入：需要足够的USDT
                total_cost = quantity * current_price * (1 + self.fee_rate)
                
                if total_cost > self.usdt_holding:
                    return OrderResult(error=f"Insufficient USDT balance. Need: {total_cost:.2f}, Have: {self.usdt_holding:.2f}")
                
                # 执行买入
                self.usdt_holding -= total_cost
                self.holding += quantity
                
                return OrderResult(
                    order_id=self.order_id,
                    status='FILLED',
                    executed_qty=quantity,
                    cummulative_quote_qty=quantity * current_price
                )
                
            elif side.upper() == 'SELL':
                # 卖出：需要足够的持仓
                if quantity > self.holding:
                    return OrderResult(error=f"Insufficient holdings. Need: {quantity:.8f}, Have: {self.holding:.8f}")
                
                # 执行卖出
                proceeds = quantity * current_price * (1 - self.fee_rate)
                self.holding -= quantity
                self.usdt_holding += proceeds
                
                return OrderResult(
                    order_id=self.order_id,
                    status='FILLED',
                    executed_qty=quantity,
                    cummulative_quote_qty=quantity * current_price
                )
            
            else:
                return OrderResult(error=f"Unknown side: {side}. Must be 'BUY' or 'SELL'.")
                
        except self.BinanceAPIException as e:
            return OrderResult(error=f"Binance API error: {e}")
    
    def get_account_info(self, symbol: str) -> AccountInfo:
        """Get current account information"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            # 计算账户总价值（USDT + 持仓价值）
            account_total = self.usdt_holding + (self.holding * current_price)
            
            return AccountInfo(
                holding=self.holding,
                usdt_holding=self.usdt_holding,
                account_total=account_total
            )
            
        except self.BinanceAPIException as e:
            print(f"Error getting account info: {e}")
            raise

class TradingBot:
    """Trading bot that uses OpenAI API to make trading decisions"""
    
    def __init__(
        self, 
        binance_api_key: str, 
        binance_api_secret: str, 
        openai_api_key: str, 
        model_name: str = "gpt-4o-mini",
        symbol: str = "BTCUSDT",
        initial_usdt: float = 300000.0,
        bot_name: str = "default"
    ):
        """Initialize trading bot"""
        self.client = PaperTradingClient(binance_api_key, binance_api_secret, initial_usdt)
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.model_name = model_name
        self.symbol = symbol
        self.bot_name = bot_name
        
        # 创建dataset文件夹（如果不存在）
        dataset_dir = "data"
        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)
        
        # 交易历史记录 - 修改路径到dataset文件夹
        self.trade_history_file = os.path.join(dataset_dir, f"{bot_name}_trade_history.csv")
        self.account_history_file = os.path.join(dataset_dir, f"{bot_name}_account_history.csv")
        
        # 初始化交易历史文件
        if not os.path.exists(self.trade_history_file):
            with open(self.trade_history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'action', 'price', 'quantity', 'value', 'usdt_balance', 'holding', 'total_value'])
        
        # 初始化账户历史文件
        if not os.path.exists(self.account_history_file):
            with open(self.account_history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'usdt_balance', 'holding', 'price', 'total_value'])
        
        print(f"Trading bot '{bot_name}' initialized with model: {model_name}")
    
    def analyze_market(self) -> Tuple[str, float, float]:
        """Analyze market using OpenAI API and return trading decision"""
        indicator, indicator_name = self.client.get_market_data(self.symbol)
        account_info = self.client.get_account_info(self.symbol)
        
        # 构建更直接的提示
        prompt = f"""
        You are a professional fund manager tasked with maximizing profits on {self.symbol} trading. Your ONLY goal is to maximize returns.
        
        Current market data for {self.symbol}:
        """
        
        for i, name in enumerate(indicator_name):
            prompt += f"{name}: {indicator[i]}\n"
        
        prompt += f"""
        Current account status:
        USDT balance: {account_info.usdt_holding:.2f}
        {self.symbol.replace('USDT', '')} holding: {account_info.holding:.8f}
        Total account value: {account_info.account_total:.2f} USDT
        
        As a profit-maximizing fund manager, provide ONLY your trading decision in this exact format:
        DECISION: [BUY, SELL, or HOLD]
        CONFIDENCE: [Number between 0 and 1]
        QUANTITY: [Percentage of available funds/holdings to use, between 0 and 1]
        Your each trade cost is 0.1% of your total trade value. 
        Do not include any explanations, reasoning, or additional text. Your response must contain ONLY these three lines.
        """
        
        try:
            # 调用OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a profit-maximizing cryptocurrency fund manager. Provide only the requested decision format without explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100  # 减少token数量，因为我们只需要简短的回复
            )
            
            # 解析响应
            response_text = response.choices[0].message.content
            
            # 提取决策、置信度和数量
            decision = "HOLD"
            confidence = 0.0
            quantity_percent = 0.0
            
            for line in response_text.split('\n'):
                if line.startswith("DECISION:"):
                    decision_text = line.replace("DECISION:", "").strip().upper()
                    if decision_text in ["BUY", "SELL", "HOLD"]:
                        decision = decision_text
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.replace("CONFIDENCE:", "").strip())
                        confidence = max(0.0, min(1.0, confidence))  # 确保在0-1之间
                    except:
                        confidence = 0.5
                elif line.startswith("QUANTITY:"):
                    try:
                        quantity_text = line.replace("QUANTITY:", "").strip()
                        # 尝试提取百分比或小数
                        if "%" in quantity_text:
                            quantity_percent = float(quantity_text.replace("%", "")) / 100.0
                        else:
                            quantity_percent = float(quantity_text)
                        quantity_percent = max(0.0, min(1.0, quantity_percent))  # 确保在0-1之间
                    except:
                        quantity_percent = 0.1  # 默认10%
            
            print(f"[{self.bot_name}] Decision: {decision}, Confidence: {confidence:.2f}, Quantity: {quantity_percent:.2f}")
            return decision, confidence, quantity_percent
            
        except Exception as e:
            print(f"Error analyzing market: {e}")
            return "HOLD", 0.0, 0.0

    
    def execute_decision(self, decision: str, quantity_percent: float) -> bool:
        """Execute trading decision"""
        if decision == "HOLD":
            return True
        
        try:
            account_info = self.client.get_account_info(self.symbol)
            current_price = self.client.get_market_data(self.symbol)[0][0]  # 获取当前价格
            
            if decision == "BUY":
                # 计算购买数量
                usdt_to_spend = account_info.usdt_holding * quantity_percent
                quantity = usdt_to_spend / current_price
                
                # 执行买入
                result = self.client.execute_trade(quantity, self.symbol, "BUY")
                
                if result.error:
                    print(f"[{self.bot_name}] Buy error: {result.error}")
                    return False
                
                # 只有在交易成功时才记录
                if result.status == 'FILLED':
                    self.record_trade("BUY", current_price, quantity, usdt_to_spend)
                    print(f"[{self.bot_name}] Bought {quantity:.8f} {self.symbol} at {current_price:.2f}")
                    return True
                else:
                    print(f"[{self.bot_name}] Buy failed: Order status {result.status}")
                    return False
                    
            elif decision == "SELL":
                # 计算卖出数量
                quantity = account_info.holding * quantity_percent
                value = quantity * current_price
                
                # 执行卖出
                result = self.client.execute_trade(quantity, self.symbol, "SELL")
                
                if result.error:
                    print(f"[{self.bot_name}] Sell error: {result.error}")
                    return False
                
                # 只有在交易成功时才记录
                if result.status == 'FILLED':
                    self.record_trade("SELL", current_price, quantity, value)
                    print(f"[{self.bot_name}] Sold {quantity:.8f} {self.symbol} at {current_price:.2f}")
                    return True
                else:
                    print(f"[{self.bot_name}] Sell failed: Order status {result.status}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"[{self.bot_name}] Error executing decision: {e}")
            return False

    
    def record_trade(self, action: str, price: float, quantity: float, value: float):
        """Record trade in history file"""
        try:
            account_info = self.client.get_account_info(self.symbol)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.trade_history_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, 
                    action, 
                    price, 
                    quantity, 
                    value, 
                    account_info.usdt_holding, 
                    account_info.holding, 
                    account_info.account_total
                ])
            print(f"[{self.bot_name}] Trade recorded: {action} {quantity:.8f} at {price:.2f}")
            
        except Exception as e:
            print(f"[{self.bot_name}] Error recording trade: {e}")
            # 不抛出异常，避免影响主程序运行

        
    def record_account_status(self):
        """Record current account status"""
        try:
            account_info = self.client.get_account_info(self.symbol)
            current_price = self.client.get_market_data(self.symbol)[0][0]  # 获取当前价格
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.account_history_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, 
                    account_info.usdt_holding, 
                    account_info.holding, 
                    current_price, 
                    account_info.account_total
                ])
            
        except Exception as e:
            print(f"[{self.bot_name}] Error recording account status: {e}")
            # 不抛出异常，避免影响主程序运行

    
    def run_trading_cycle(self):
        """Run a single trading cycle"""
        try:
            # 分析市场
            decision, confidence, quantity_percent = self.analyze_market()
            
            # 执行决策
            if confidence >= 0.5:  # 只有当置信度大于0.5时才执行
                success = self.execute_decision(decision, quantity_percent)
                if not success:
                    print(f"[{self.bot_name}] Decision execution failed, skipping this cycle")
            
            # 只有在没有错误的情况下才记录账户状态
            self.record_account_status()
            
        except Exception as e:
            print(f"[{self.bot_name}] Error in trading cycle: {e}")
            print(f"[{self.bot_name}] Skipping data recording for this cycle")

    
    def run(self, cycles: int = 1, interval: int = 60):
        """Run trading bot for specified number of cycles"""
        print(f"[{self.bot_name}] Starting trading bot with {cycles} cycles, interval {interval} seconds")
        
        for i in range(cycles):
            print(f"[{self.bot_name}] Cycle {i+1}/{cycles}")
            self.run_trading_cycle()
            
            if i < cycles - 1:  # 不在最后一个周期后等待
                time.sleep(interval)
        
        print(f"[{self.bot_name}] Trading completed")
