import akshare as ak
import pandas as pd
from datetime import datetime
import os

class StockPriceMonitor:
    def __init__(self):
        """
        初始化，获取股票代码和名称的映射。
        """
        print("开始初始化，获取股票代码和名称的映射...")
        self.stock_info_sh = ak.stock_info_sh_name_code()  # 上海交易所
        self.stock_info_sz = ak.stock_info_sz_name_code()  # 深圳交易所
        if self.stock_info_sh.empty or self.stock_info_sz.empty:
            print("初始化失败，未能获取到完整股票代码和名称的映射信息，程序终止。")
            exit(1)
        self.code_name_map_sh = dict(zip(self.stock_info_sh['证券代码'], self.stock_info_sh['证券简称']))
        self.code_name_map_sz = dict(zip(self.stock_info_sz['A股代码'], self.stock_info_sz['A股简称']))
        self.all_stocks_data = {}  # 存储所有股票前复权数据的dict，key=股票代码，value=DataFrame
        self.load_stock_data_from_csv()  # 尝试从 CSV 文件加载数据
        self.iterate_over_all_stocks()
        print("初始化完成。")

    def iterate_over_all_stocks(self):
        """
        遍历所有股票，获取前复权日线数据。
        :return: 包含日期、开盘价、最高价、最低价、收盘价成交量、成交额和换手率的 DataFrame
        """
        print("开始遍历所有股票，获取前复权日线数据...")
        # 上海交易所的股票
        for code, name in self.code_name_map_sh.items():
            if code in self.all_stocks_data:
                print(f"股票代码 {code} 数据已从本地加载，跳过获取。")
                continue
            print(f"正在获取股票代码：{code}，名称：{name} 的日线数据...")
            df = self.fetch_price_data("sh" + code)
            if df is None:
                print(f"股票代码 {code} 不存在于数据集中。")
                continue
            kdj_data = self.calculate_kdj(df)  # 计算KDJ指标
            df = pd.merge(df, kdj_data, on='date')
            self.all_stocks_data[code] = df
            self.save_single_stock_data_to_csv(code, df)
            print(f"股票代码 {code} 的前复权日线数据获取完成。")
        # 深圳交易所的股票
        for code, name in self.code_name_map_sz.items():
            if code in self.all_stocks_data:
                print(f"股票代码 {code} 数据已从本地加载，跳过获取。")
                continue
            print(f"正在获取股票代码：{code}，名称：{name} 的日线数据...")
            df = self.fetch_price_data("sz" + code)
            if df is None:
                print(f"股票代码 {code} 不存在于数据集中。")
                continue
            kdj_data = self.calculate_kdj(df)  # 计算KDJ指标
            df = pd.merge(df, kdj_data, on='date')
            self.all_stocks_data[code] = df
            self.save_single_stock_data_to_csv(code, df)
            print(f"股票代码 {code} 的前复权日线数据获取完成。")
        print("所有股票前复权日线数据获取完成。")

    @staticmethod
    def fetch_price_data(stock_code):
        """
        获取单支股票前复权日线数据。
        :param stock_code: 股票代码
        :return: 包含日期、开盘价、最高价、最低价、收盘价成交量、成交额和换手率的 DataFrame
        """
        df = ak.stock_zh_a_daily(symbol=stock_code,
                                 start_date="19910101",
                                 end_date=datetime.today().strftime("%Y%m%d"),
                                 adjust="qfq")
        return df[["date", "open", "high", "low", "close", "volume", "amount", "turnover"]]

    def get_stock_data(self, stock_code):
        """
        获取单支股票的前复权日线数据。
        :param stock_code: 股票代码
        :return: 包含日期、开盘价、最高价、最低价、收盘价成交量、成交额和换手率的 DataFrame
        """
        if stock_code not in self.all_stocks_data:
            print(f"股票代码 {stock_code} 不存在于数据集中。")
            return None
        return self.all_stocks_data.get(stock_code)

    def get_all_stocks_data(self):
        """
        获取所有股票的前复权日线数据。
        :return: key=股票代码，value=包含日期、开盘价、最高价、最低价、收盘价成交量、成交额和换手率的 DataFrame
        """
        return self.all_stocks_data

    @staticmethod
    def calculate_kdj(stock_df, n=9, m=3):
        """
        计算KDJ指标。
        :param stock_df: 包含股票价格数据的 DataFrame
        :param n: RSV计算的周期，默认为9
        :param m: K、D计算的平滑系数，默认为3
        :return: 包含日期、K、D、J值的 DataFrame
        """
        df = stock_df.copy()    # 复制数据，避免修改原始数据
        # 计算RSV值
        low_list = df['low'].rolling(n).min()
        high_list = df['high'].rolling(n).max()  # 计算最高价的滚动窗口
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100
        # 计算K,D,J值
        df['K'] = rsv.ewm(alpha=1 / m, adjust=False).mean()
        df['D'] = df['K'].ewm(alpha=1 / m, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        return df[['date', 'K', 'D', 'J']]

    @staticmethod
    def generate_signal(df):
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

    def save_single_stock_data_to_csv(self, code, df):
        """
        将单支股票数据保存到 CSV 文件。
        """
        if not os.path.exists('stock_data'):
            os.makedirs('stock_data')
        df.to_csv(f'stock_data/{code}.csv', index=False)

    def load_stock_data_from_csv(self):
        """
        从 CSV 文件加载所有股票数据。
        """
        if os.path.exists('stock_data'):
            for file in os.listdir('stock_data'):
                if file.endswith('.csv'):
                    code = file.replace('.csv', '')
                    self.all_stocks_data[code] = pd.read_csv(f'stock_data/{file}')


if __name__ == "__main__":
    # 初始化，获取所有个股的前复权日线数据
    monitor = StockPriceMonitor()

    # 输出买卖信号
    for code, df in monitor.get_all_stocks_data().items():
        signal_type, msg = monitor.generate_signal(df)
        if signal_type != "HOLD":
            print(f"股票代码：{code}，信号类型：{signal_type}，{msg}")