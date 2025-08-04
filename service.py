# stock_api.py (简化版)
from flask import Flask, jsonify, request
import akshare as ak
import pandas as pd
import logging
from datetime import datetime

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('StockAPI')

def get_latest_price(symbol, market):
    """获取股票最新收盘价"""
    try:
        # 获取最新数据（默认返回最新交易日数据）
        if market.lower() == 'hk':
            # 使用working的港股API
            df = ak.stock_hk_hist(symbol=symbol, period="daily", start_date="20240101", end_date="20241201")
            # 港股数据使用中文列名
            latest = df.iloc[-1]  # 获取最新一条记录
            date_str = latest['日期']
            close_price = latest['收盘']
        elif market.lower() == 'us':
            df = ak.stock_us_daily(symbol=symbol, adjust="qfq")
            # 美股数据使用英文列名
            latest = df.sort_index(ascending=False).iloc[0]
            # 检查索引是否为datetime类型
            if hasattr(latest.name, 'strftime'):
                date_str = latest.name.strftime('%Y-%m-%d')
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
            close_price = latest['close']
        else:
            return None, "Invalid market type"
        
        return {
            "symbol": symbol,
            "market": market,
            "date": date_str,
            "close": close_price
        }, None
        
    except Exception as e:
        logger.error(f"Error fetching latest price for {symbol}: {str(e)}")
        return None, str(e)

@app.route('/api/stock/latest_price', methods=['GET'])
def latest_price():
    """获取最新收盘价端点"""
    symbol = request.args.get('symbol')
    market = request.args.get('market')
    
    if not symbol or not market:
        return jsonify({"error": "Missing symbol or market"}), 400
    
    data, error = get_latest_price(symbol, market)
    
    if error:
        return jsonify({"error": error}), 500
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)