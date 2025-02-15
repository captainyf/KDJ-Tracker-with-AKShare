import akshare as ak
import pandas as pd
from datetime import datetime

# ========== 个股代码 ==========
STOCK_CODES = ["sh600519",  # 贵州茅台
               "sz000858",  # 五粮液
               "sh600030",  # 中信证券
               "sz000776",  # 广发证券
               "sh600570",  # 恒生电子
               ]
# ===========================


class StockMonitor:
    def __init__(self):
        """
        初始化 StockMonitor 类，获取股票代码和名称的映射。
        """
        print("开始初始化，获取股票代码和名称的映射...")
        self.stock_info = ak.stock_info_a_code_name()
        if self.stock_info.empty:
            print("未能获取到股票代码和名称的映射信息，程序终止。")
            exit(1)
        self.code_name_map = dict(zip(self.stock_info['code'], self.stock_info['name']))

    def fetch_stock_data(self, stock_code):
        """
        获取无复权日线数据。
        :param stock_code: 股票代码
        :return: 包含日期、开盘价、最高价、最低价、收盘价和成交量的 DataFrame
        """
        df = ak.stock_zh_a_daily(symbol=stock_code,
                                 start_date="19910403",
                                 end_date=datetime.today().strftime("%Y%m%d"),
                                 adjust="")
        return df[["date", "open", "high", "low", "close", "amount"]]

    def calculate_kdj(self, data, n=9, m=3):
        """
        手动计算KDJ指标。
        :param data: 包含股票价格数据的 DataFrame
        :param n: RSV计算的周期，默认为9
        :param m: K、D计算的平滑系数，默认为3
        :return: 包含日期、K、D、J值的 DataFrame
        """
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

    def generate_signal(self, df):
        """
        生成交易信号。
        :param df: 包含KDJ指标的 DataFrame
        :return: 交易信号类型和信号信息
        """
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

    def process_stock(self, stock_code):
        """
        处理单只股票，包括数据获取、KDJ计算、信号生成和结果打印。
        :param stock_code: 股票代码
        """
        print(f"正在处理股票代码：{stock_code}...")
        # 数据获取与计算
        print("正在获取股票价格数据...")
        price_data = self.fetch_stock_data(stock_code)
        if price_data.empty:
            print(f"未能获取到 {stock_code} 的价格数据，跳过该股票。")
            return

        print("正在计算KDJ指标...")
        kdj_data = self.calculate_kdj(price_data)

        if kdj_data.empty:
            print(f"未能计算出 {stock_code} 的KDJ指标，跳过该股票。")
            return

        # 信号生成
        print("正在合并数据并生成交易信号...")
        merged_df = pd.merge(price_data, kdj_data, on='date')
        signal_type, msg = self.generate_signal(merged_df)
        latest_j = merged_df.iloc[-1]['J']

        # 获取股票名称
        stock_name = self.code_name_map.get(stock_code[2:], "未知名称")

        # 打印结果
        if signal_type != "HOLD":
            print(f"股票代码：{stock_code[2:]}，股票名称：{stock_name}\n信号类型：{signal_type}\n{msg}\n当前J值：{latest_j:.2f}")
        else:
            print(f"股票代码：{stock_code[2:]}，股票名称：{stock_name} 今日无交易信号，当前J值：{latest_j:.2f}")
        print("-" * 50)

    def run(self):
        """
        运行股票监控程序，处理所有配置的股票代码。
        """
        for stock_code in STOCK_CODES:
            self.process_stock(stock_code)


if __name__ == "__main__":
    monitor = StockMonitor()
    monitor.run()
