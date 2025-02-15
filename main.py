"""
main.py - 股票数据监控与交易信号系统
"""
import akshare as ak
import pandas as pd
from datetime import datetime

# ========== 配置区 ==========
STOCK_CODES = ["sh600519",  # 贵州茅台
               "sz000858",  # 五粮液
               "sh600030",  # 中信证券
               "sz000776",  # 广发证券
               "sh600570",  # 恒生电子
               ]

# ===========================


def fetch_stock_data(stock_code):
    """获取无复权日线数据"""
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
    if df.empty:
        print("输入的DataFrame为空，无法生成交易信号。")
        return "HOLD", None
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # J值超买超卖判断
    buy_signal = (latest.J < 20) and (prev.J <= latest.J)
    sell_signal = (latest.J > 80) and (prev.J >= latest.J)

    if buy_signal:
        return "BUY", f"{latest['date']} J值触底回升：{latest.J:.2f}"
    elif sell_signal:
        return "SELL", f"{latest['date']} J值见顶回落：{latest.J:.2f}"
    return "HOLD", None


if __name__ == "__main__":
    # 获取股票代码和名称的映射
    print("正在获取股票代码和名称的映射...")
    stock_info = ak.stock_info_a_code_name()
    if stock_info.empty:
        print("未能获取到股票代码和名称的映射信息，程序终止。")
        exit(1)
    code_name_map = dict(zip(stock_info['code'], stock_info['name']))

    for STOCK_CODE in STOCK_CODES:
        print(f"正在处理股票代码：{STOCK_CODE}...")
        # 数据获取与计算
        print("正在获取股票价格数据...")
        price_data = fetch_stock_data(STOCK_CODE)
        if price_data.empty:
            print(f"未能获取到 {STOCK_CODE} 的价格数据，跳过该股票。")
            continue
        print("正在计算KDJ指标...")
        kdj_data = calculate_kdj(price_data)
        if kdj_data.empty:
            print(f"未能计算出 {STOCK_CODE} 的KDJ指标，跳过该股票。")
            continue

        # 信号生成
        print("正在合并数据并生成交易信号...")
        merged_df = pd.merge(price_data, kdj_data, on='date')
        signal_type, msg = generate_signal(merged_df)
        latest_j = merged_df.iloc[-1]['J']

        # 获取股票名称
        stock_name = code_name_map.get(STOCK_CODE[2:], "未知名称")

        # 打印结果
        if signal_type != "HOLD":
            print(f"股票代码：{STOCK_CODE[2:]}，股票名称：{stock_name}\n信号类型：{signal_type}\n{msg}\n当前J值：{latest_j:.2f}")
        else:
            print(f"股票代码：{STOCK_CODE[2:]}，股票名称：{stock_name} 今日无交易信号，当前J值：{latest_j:.2f}")
        print("-" * 50)
