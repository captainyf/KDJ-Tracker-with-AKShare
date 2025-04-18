# Stock-Indicator-Monitor

一个爬取A股个股K线数据、计算KDJ指标的Python示例，基于akshare框架开发。
A Python example for crawling A-share individual stock K-line data and calculating the KDJ indicator, developed based on the akshare framework.

# Background
东方财富、同花顺等平台提供的免费**指标监控**功能和**数据分析**功能有限，无法满足个性化的指标跟踪和交易信号自动提醒的需求。因此决定开发本项目，用于辅助获取**交易性**的投资机会。

Platforms like ​​East Money​​ (东方财富) and ​​Tonghuashun​​ (同花顺) offer limited ​​indicator monitoring​​ and ​​data analysis​​ features for free, which cannot meet the demand for ​​personalized indicator tracking​​ and ​​automatic trading signal alerts​​. Therefore, this project was developed to assist in identifying ​​trading-oriented​​ investment opportunities.


另外，**结构性**的投资机会需要结合**宏观政策**和**公司基本面**分析，借助多模态大模型Agent理应能取得一定效果，但不在本项目的范围内。

Additionally, ​​structural​​ investment opportunities require analysis combining ​​macroeconomic policies​​ and ​​company fundamentals​​. While multimodal large-model Agents could be effective in this regard, such analysis falls outside the scope of this project.

# Progress
## 抓取日线数据
- [x] 抓取个股日线级别K线的数据，历史数据一次性获取
- [x] 批量获取个股列表
- [x] 股票数据本地缓存，存储到csv文件
- [x] 增加个股数据的增量更新功能
## 计算技术指标
- [x] 计算日线的KDJ指标
## 判断买卖信号
- [x] 基于日线的KDJ指标的买卖信号提示
