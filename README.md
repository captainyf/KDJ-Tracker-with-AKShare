# Stock-Indicator-Monitor

一个监控A股个股技术指标的Python应用

# 项目背景
东方财富、同花顺等平台提供的**指标监控**功能和**数据分析**功能有限，无法充分满足个性化的指标跟踪和辅助交易决策的需求，因此决定开发本项目。

# 功能开发进度
- [x] 抓取个股日线级别K线的数据，历史数据一次性获取
- [x] 计算技术指标，目前仅包括KDJ
- [x] 根据指标判断交易买卖点
- [ ] Web服务推送指标分析结果 
- [ ] 存储单次请求数据到数据库
- [ ] 提供个股数据的全量更新和增量更新功能
- [ ] 开发简易的量化交易策略
- [ ] 开发回测交易策略的功能