# coding=utf-8
"""
第一个策略：先计算过去90日内处于目标价格区间[0, a]的天数（down）,
和处于区间[1.1a, max]的天数(up)，再计算比值up/down，决定买入或卖出
"""
from ctaBase import *
from ctaTemplate import CtaTemplate

class Up2downRate(CtaTemplate):
    """高低比率策略"""
    className = 'Up2DownRate'
    author = 'greglchen'

    # 策略参数
    priceType = 'C'     # OHLC中的某一种价格
    beta = 1.1          # 价格浮动区间
    highRate = 1.2   # up/down的临界值，高于此值买入
    lowRate = 0.1    # up/down的临界值，低于此值卖出
    lookbackDays = 60  # 回测区间长度

    # 策略变量
    bar = None
    barDay = EMPTY_STRING
    secId = EMPTY_STRING   #股票ID
    upDays = EMPTY_INT     # up日期天数
    downDays = EMPTY_INT   # down日期天数
    preBars = None         # 最近的行情BAR DATAFRAME

    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'priceType',
                 'beta',
                 'highRate',
                 'lowRate',
                 'lookbackDays']

    varList = ['inited',
               'trading',
               'pos',
               'secId',
               'upDays',
               'downDays']

    def __init__(self, ctaEngine, setting):
        super(Up2downRate, self).__init__(ctaEngine, setting)
        self.upDays = 0
        self.downDays = 0
        self.secId = ''
        self.preBars = None
        self.barDbName = 'DAY_PUFA_TRADE'
        self.vtSymbol = 'PUFA10TO16'

    def getUpDownDays(self, barList, initPrice):
        upDays = 0
        downDays = 0
        for bar in barList:
            if bar.high >= initPrice * self.beta:
                upDays += 1
            elif bar.low <= initPrice:
                downDays += 1
        return upDays, downDays

    def onInit(self):
        self.writeCtaLog(u'UP2DOWN策略初始化')

        self.preBars = self.loadBar(self.lookbackDays)
        if self.priceType == 'C':
             initPrice = self.preBars[-1].close
        self.upDays, self.downDays = self.getUpDownDays(self.preBars, initPrice)
        self.putEvent()

    def onStart(self):
        self.writeCtaLog(u'UP2DOWN策略启动')
        self.putEvent()

    def onStop(self):
        self.writeCtaLog(u'UP2DOWN策略停止')
        self.putEvent()

    def onTick(self, tick):
        pass

    def onBar(self, bar):
        # 计算最新的U/D比例

        self.preBars = self.preBars[1:]
        self.preBars.append(bar)
        if self.priceType == 'C':
            lastPrice = bar.close
        self.upDays, self.downDays = self.getUpDownDays(self.preBars, lastPrice)
        upDownRate = 1.0 * self.upDays / self.downDays if self.downDays != 0 else self.upDays

        # 判断买卖
        belowRate =  upDownRate < self.lowRate
        aboveRate = upDownRate > self.highRate

        if belowRate:
            if self.pos > 0:
                self.sell(bar.close, 1)
        elif aboveRate:
            if self.pos == 0:
                self.buy(bar.close, 1)

        self.putEvent()

    def onOrder(self, order):
        pass

    def onTrade(self, trade):
        pass










