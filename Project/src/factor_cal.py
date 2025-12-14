

import sys
import os
import numpy as np
# 添加Project目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_load import load_stock_data, get_all_stock_codes


class StockFactorCalculator:
    def __init__(self, stock_list: list = None):
        self.stock_list = stock_list or get_all_stock_codes()
        self.data_cache = {}
        self.results = {}

    def _load_data(self, stock_code: str, data_type: str):
         key = f"{stock_code}_{data_type}"
         if key not in self.data_cache:
                self.data_cache[key] = load_stock_data(stock_code, data_type)
         return self.data_cache[key]

    #上午&下午成交量比值
    def calc_volume_ratio(self):
        for stock_code in self.stock_list:
            df_transaction = self._load_data(stock_code, 'transaction')
            if df_transaction is None or df_transaction.empty:
                print(f"股票 {stock_code} 的逐笔成交数据为空，跳过计算。")
                continue
                
                # 提取相关列数据
            time_vals = df_transaction['时间'].values
            code_vals = df_transaction['成交代码'].values  
            order_vals = df_transaction['叫买序号'].values
            volume_vals = df_transaction['成交数量'].values

            ###考虑上交所的筛选条件
            if stock_code.endswith(".SZ"):
                valid_trade = (code_vals == '0')
            else:
                valid_trade = np.ones(len(code_vals), dtype=bool)


                # 筛选条件
            mask_morning = (
                    (time_vals >= 92500000) & 
                    (time_vals < 100000000) & 
                    (valid_trade) & 
                    (order_vals != 0)
                )

            mask_afternoon = (
                    (time_vals >= 130000000) & 
                    (time_vals < 133000000) & 
                    (valid_trade) & 
                    (order_vals != 0)
                )

            # 计算结果
            volume_morning = volume_vals[mask_morning].sum()
            volume_afternoon = volume_vals[mask_afternoon].sum()
                
            if volume_afternoon == 0:
                print(f"股票 {stock_code} 上午成交量为0，无法计算比率。")
                continue
                
            volume_ratio =  volume_morning / volume_afternoon 
            print(f"股票 {stock_code} 下午成交量与上午成交量的比率为: {volume_ratio:.4f}")

            if stock_code not in self.results:
                self.results[stock_code] = {}
            
            self.results[stock_code]['volume_ratio'] = volume_ratio

    ##主动买卖占比
    def calc_act_ratio(self):
        for stock_code in self.stock_list:
            try:
                df_market = self._load_data(stock_code, 'transaction')
                if df_market is None or df_market.empty:
                    print(f"股票 {stock_code} 的市场数据为空，跳过计算。")
                    continue

                # if stock_code.endswith(".SH"):
                #     continue

                df_market = df_market[
                    (df_market["成交代码"] == '0') | (df_market["成交代码"].isna())
                ]

                if df_market.empty:
                    print(f"{stock_code} 无法计算 ACT（无有效成交）")
                    if stock_code not in self.results:
                        self.results[stock_code] = {}
                    self.results[stock_code]['act_ratio'] = np.nan
                    continue

                df_market = df_market[df_market["时间"] >= 93000000]
                ###assign只用来造列
                df_market = df_market.assign(
                            amount=(df_market["成交价格"] * df_market["成交数量"])/10000,
                            side=df_market["BS标志"].map({'B': 'Buy', 'S': 'Sell'})
                        )

                df_market = df_market[df_market["side"].notna()]

                df_market["size"] = np.select(
                        [df_market["amount"] > 1e6,
                        (df_market["amount"] > 2e5) & (df_market["amount"] <= 1e6),
                        (df_market["amount"] > 4e4) & (df_market["amount"] <= 2e5),
                        (df_market["amount"] <= 4e4)],
                        ["X", "L", "M", "S"],
                        default="S"
                    )

                                # ===== 直接算 daily（不建 minute 表）=====
                daily_amt = (
                            df_market
                            .groupby(["size", "side"], sort=False)["amount"]
                            .sum()
                            .unstack(fill_value=0)
                        )

                buy_amt  = daily_amt["Buy"].sum()
                sell_amt = daily_amt["Sell"].sum()
                ACT = (buy_amt - sell_amt) / (buy_amt + sell_amt + 1e-12)

                def calc_act(row):
                    return (row["Buy"] - row["Sell"]) / (row["Buy"] + row["Sell"] + 1e-12)

                result = {
                            k: calc_act(daily_amt.loc[k])
                            for k in daily_amt.index
                        }

                print(
                            f"{stock_code} ACT={ACT:.4f}, "
                            + ", ".join(f"{k}_ACT={v:.4f}" for k, v in result.items())
                        )
                
                #self.results[stock_code]['ACT'] = result
                self.results[stock_code]['act_ratio'] = {
                        'overall': ACT,        # 整体ACT
                        'by_size': result      # 分规模ACT
                    }
            except Exception as e:
                print(f"计算股票 {stock_code} 的ACT时出错: {e}")


    ##订单占比_深交所
    def calc_order_sz_ratio(self):
         for stock_code in self.stock_list:
            try:
                if not stock_code.endswith(".SZ"):
                    continue

                df_order = self._load_data(stock_code, 'order')
                if df_order is None or df_order.empty:
                        print(f"股票 {stock_code} 的委托数据为空，跳过计算。")
                        continue
                    
                df_order = df_order[df_order["时间"] >= 91500000]

                df_order = df_order.assign(
                        minute = df_order["时间"] // 100000,
                        amount = (df_order["委托价格"] * df_order["委托数量"])/10000,
                        side = df_order["委托代码"].map({'B': 'Buy', 'S': 'Sell'})
                    )

                df_order["size"] = np.select(
                        [df_order["amount"] > 1e6,
                        (df_order["amount"] > 2e5) & (df_order["amount"] <= 1e6),
                        (df_order["amount"] > 4e4) & (df_order["amount"] <= 2e5),
                        (df_order["amount"] <= 4e4)],
                        ["X", "L", "M", "S"],
                        default="S"
                    )

                daily_amt = (
                            df_order
                            .groupby(["size", "side"], sort=False)["amount"]
                            .sum()
                            .unstack(fill_value=0)
                        )
                    
                buy_amt = daily_amt["Buy"].sum()
                sell_amt = daily_amt["Sell"].sum()
                    
                def calc_act(row):
                        return (row["Buy"] + row["Sell"]) / (buy_amt + sell_amt + 1e-12)
                    
                result = {
                            k: calc_act(daily_amt.loc[k])
                            for k in daily_amt.index
                    }

                print(
                        f"{stock_code} 委托量比率 Buy={buy_amt:.2f}, Sell={sell_amt:.2f}, "
                        + ", ".join(f"{k}_ACT={v:.4f}" for k, v in result.items())
                    )

                #self.results[stock_code]['order_ratio'] = result
                self.results[stock_code]['order_ratio'] = {
                    'buy_total': buy_amt,
                    'sell_total': sell_amt,
                    'by_size': result
                }
            except Exception as e:
                print(f"计算股票 {stock_code} 的委托量比率时出错: {e}")

    ##订单占比_上交所
    def calc_order_sh_ratio(self):
        for stock_code in self.stock_list:
            try:
                if not stock_code.endswith(".SH"):
                    continue

                df_order = self._load_data(stock_code, 'order')
                if df_order is None or df_order.empty:
                    continue
                
                # 1️⃣ 连续竞价
                df_order = df_order[df_order["时间"] >= 91500000]

                # 2️⃣ 只保留挂单
                df_order = df_order[df_order["委托类型"] == 'A']

                # 3️⃣ 买卖方向
                df_order["side"] = df_order["委托代码"].map({'B': 'Buy', 'S': 'Sell'})
                df_order = df_order[df_order["side"].notna()]
                # 4️⃣ 金额还原
                df_order["amount"] = df_order["委托价格"] / 10000.0 * df_order["委托数量"]

                # 5️⃣ 大小单划分
                df_order["size"] = np.select(
                    [
                        df_order["amount"] > 1e6,
                        (df_order["amount"] > 2e5) & (df_order["amount"] <= 1e6),
                        (df_order["amount"] > 4e4) & (df_order["amount"] <= 2e5),
                        (df_order["amount"] <= 4e4)
                    ],
                    ["X", "L", "M", "S"]
                )

                daily_amt = (
                    df_order.groupby(["size", "side"])["amount"]
                    .sum()
                    .unstack(fill_value=0)
                )
                buy_amt = daily_amt["Buy"].sum()
                sell_amt = daily_amt["Sell"].sum()
                    

                total_amt = daily_amt.sum().sum()
                if stock_code not in self.results:
                    self.results[stock_code] = {}

                def calc_act(row):
                        return (row["Buy"] + row["Sell"]) / (buy_amt + sell_amt + 1e-12)

                result = {
                            k: calc_act(daily_amt.loc[k])
                            for k in daily_amt.index
                    }

                print(
                        f"{stock_code} 委托量比率 Buy={buy_amt:.2f}, Sell={sell_amt:.2f}, "
                        + ", ".join(f"{k}_ACT={v:.4f}" for k, v in result.items())
                    )


                self.results[stock_code]['order_ratio'] = {
                        'buy_total': buy_amt,
                        'sell_total': sell_amt,
                        'by_size': result
                    }

            except Exception as e:
                print(f"计算股票 {stock_code} 的委托量比率时出错: {e}")

    def calc_all(self):  ##计算所有因子
        self.calc_volume_ratio()
        self.calc_act_ratio()
        self.calc_order_sz_ratio()
        self.calc_order_sh_ratio()
        return self.results

    def get_results(self):
            """获取结果"""
            return self.results




# def cal_volume_ratio(stock_list: list = None):
#     if stock_list is None:
#         stock_list =  get_all_stock_codes()
    
#     for stock_code in stock_list:
#             try:
#                 df_transaction = load_stock_data(stock_code, 'transaction')
#                 if df_transaction is None or df_transaction.empty:
#                     print(f"股票 {stock_code} 的逐笔成交数据为空，跳过计算。")
#                     continue
                
#                 # 提取相关列数据
#                 time_vals = df_transaction['时间'].values
#                 code_vals = df_transaction['成交代码'].values  
#                 order_vals = df_transaction['叫买序号'].values
#                 volume_vals = df_transaction['成交数量'].values

#                 # 筛选条件
#                 mask_morning = (
#                     (time_vals >= 92500000) & 
#                     (time_vals < 100000000) & 
#                     ((code_vals == '0') |(code_vals == '') ) & 
#                     (order_vals != 0)
#                 )

#                 mask_afternoon = (
#                     (time_vals >= 130000000) & 
#                     (time_vals < 133000000) & 
#                     (code_vals == '0') & 
#                     (order_vals != 0)
#                 )

#                 # 计算结果
#                 volume_morning = volume_vals[mask_morning].sum()
#                 volume_afternoon = volume_vals[mask_afternoon].sum()
                
#                 if volume_morning == 0:
#                     print(f"股票 {stock_code} 上午成交量为0，无法计算比率。")
#                     continue
                
#                 volume_ratio =  volume_morning / volume_afternoon 
#                 print(f"股票 {stock_code} 下午成交量与上午成交量的比率为: {volume_ratio:.4f}")

#             except Exception as e:
#                 print(f"计算股票 {stock_code} 的成交量比率时出错: {e}")
        


# def cal_act_ratio(stock_list: list = None):
#     if stock_list is None:
#         stock_list =  get_all_stock_codes()
    
#     for stock_code in stock_list:
#             try:
#                 df_market = load_stock_data(stock_code, 'transaction')
#                 if df_market is None or df_market.empty:
#                     print(f"股票 {stock_code} 的市场数据为空，跳过计算。")
#                     continue
                

#                 df_market = df_market.assign(
#                         minute=df_market["时间"] // 100000,
#                         amount=df_market["成交价格"] * df_market["成交数量"],
#                         side=df_market["BS标志"].map({'B': 'Buy', 'S': 'Sell'})
#                     )

#                 df_market = df_market[df_market["side"].notna()]

#                 df_market["size"] = np.select(
#                     [df_market["amount"] > 1e6,
#                     (df_market["amount"] > 2e5) & (df_market["amount"] <= 1e6),
#                     (df_market["amount"] > 4e4) & (df_market["amount"] <= 2e5),
#                     (df_market["amount"] <= 4e4)],
#                     ["X", "L", "M", "S"],
#                     default="S"
#                 )

#                             # ===== 直接算 daily（不建 minute 表）=====
#                 daily_amt = (
#                         df_market
#                         .groupby(["size", "side"], sort=False)["amount"]
#                         .sum()
#                         .unstack(fill_value=0)
#                     )

#                 buy_amt  = daily_amt["Buy"].sum()
#                 sell_amt = daily_amt["Sell"].sum()
#                 ACT = (buy_amt - sell_amt) / (buy_amt + sell_amt + 1e-12)

#                 def calc_act(row):
#                     return (row["Buy"] - row["Sell"]) / (row["Buy"] + row["Sell"] + 1e-12)

#                 result = {
#                         k: calc_act(daily_amt.loc[k])
#                         for k in daily_amt.index
#                     }

#                 print(
#                         f"{stock_code} ACT={ACT:.4f}, "
#                         + ", ".join(f"{k}_ACT={v:.4f}" for k, v in result.items())
#                     )
                
#             except Exception as e:
#                     print(f"计算股票 {stock_code} 的ACT时出错: {e}")


# def cal_order_ratio(stock_list: list = None):
#      if stock_list is None:
#         stock_list =  get_all_stock_codes()

#      for stock_code in stock_list:
#             try:
#                 df_order = load_stock_data(stock_code, 'order')
#                 if df_order is None or df_order.empty:
#                     print(f"股票 {stock_code} 的委托数据为空，跳过计算。")
#                     continue
                

#                 df_order = df_order.assign(
#                      minute = df_order["时间"] // 100000,
#                      amount = df_order["委托价格"] * df_order["委托数量"],
#                      side = df_order["委托代码"].map({'B': 'Buy', 'S': 'Sell'})
#                 )

#                 df_order["size"] = np.select(
#                     [df_order["amount"] > 1e6,
#                     (df_order["amount"] > 2e5) & (df_order["amount"] <= 1e6),
#                     (df_order["amount"] > 4e4) & (df_order["amount"] <= 2e5),
#                     (df_order["amount"] <= 4e4)],
#                     ["X", "L", "M", "S"],
#                     default="S"
#                 )

#                 daily_amt = (
#                         df_order
#                         .groupby(["size", "side"], sort=False)["amount"]
#                         .sum()
#                         .unstack(fill_value=0)
#                     )
                
#                 buy_amt = daily_amt["Buy"].sum()
#                 sell_amt = daily_amt["Sell"].sum()
                
#                 def calc_act(row):
#                      return (row["Buy"] - row["Sell"]) / (row["Buy"] + row["Sell"] + 1e-12)
                
#                 result = {
#                         k: calc_act(daily_amt.loc[k])
#                         for k in daily_amt.index
#                 }

#                 print(
#                      f"{stock_code} 委托量比率 Buy={buy_amt:.2f}, Sell={sell_amt:.2f}, "
#                      + ", ".join(f"{k}_ACT={v:.4f}" for k, v in result.items())
#                 )

#             except Exception as e:
#                 print(f"计算股票 {stock_code} 的委托量比率时出错: {e}")

# if __name__ == "__main__":
#         # 查看路径信息
#         print("=== 路径调试信息 ===")
#         print(f"当前工作目录: {os.getcwd()}")
#         print(f"当前文件路径: {__file__}")
#         print(f"当前文件绝对路径: {os.path.abspath(__file__)}")
#         print(f"文件所在目录: {os.path.dirname(os.path.abspath(__file__))}")
#         print(f"项目根目录: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
        
#         print("\n=== Python模块搜索路径 ===")
#         for i, path in enumerate(sys.path):
#             print(f"{i}: {path}")
        
#         print("\n=== 开始运行函数 ===")
#         cal_volume_ratio(['000001.SZ', '000002.SZ'])
#         cal_volume_ratio(['000001.SZ', '000002.SZ'])  # 示例股票代码列表