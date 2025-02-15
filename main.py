"""
main.py - 股票数据监控与交易信号系统
"""
import akshare as ak
import pandas as pd
from datetime import datetime

# ========== 配置区 ==========
STOCK_CODES = ["sh600519", "sh600000"]  # 股票代码列表

# ===========================


def fetch_stock_data(stock_code):
    """获取后复权日线数据"""
    df = ak.stock_zh_a_daily(symbol=stock_code,
                             start_date="19910403",
                             end_date=datetime.today().strftime("%Y%m%d"),
                             adjust="")

    return df[["date", "open", "high", "low", "close", "amount"]]


def calculate_kdj(data, n=9, m=3):
    """手动计算KDJ指标"""
    df = data.copy()
    # 计算RSV值
    low_list = df['low'].rolling(n).min()
    high_list = df['high'].rolling(n).max()
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100

    # 计算K,D,J值
    df['K'] = rsv.ewm(alpha=1 / m, adjust=False).mean()
    df['D'] = df['K'].ewm(alpha=1 / m, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df[['date', 'K', 'D', 'J']]


def generate_signal(df):
    """生成交易信号"""
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # J值超买超卖判断
    buy_signal = (latest.J < 20) and (prev.J <= latest.J)
    sell_signal = (latest.J > 80) and (prev.J >= latest.J)

    if buy_signal:
        return "BUY", f"{latest['日期']} J值触底回升：{latest.J:.2f}"
    elif sell_signal:
        return "SELL", f"{latest['日期']} J值见顶回落：{latest.J:.2f}"
    return "HOLD", None


if __name__ == "__main__":
    for STOCK_CODE in STOCK_CODES:
        # 数据获取与计算
        price_data = fetch_stock_data(STOCK_CODE)
        kdj_data = calculate_kdj(price_data)

        # 信号生成
        merged_df = pd.merge(price_data, kdj_data, on='date')
        signal_type, msg = generate_signal(merged_df)
        latest_j = merged_df.iloc[-1]['J']

        # 触发结果输出
        if signal_type != "HOLD":
            print(f"股票代码：{STOCK_CODE}\n信号类型：{signal_type}\n{msg}\n当前J值：{latest_j:.2f}")
        else:
            print(f"股票代码：{STOCK_CODE} 今日无交易信号，当前J值：{latest_j:.2f}")
