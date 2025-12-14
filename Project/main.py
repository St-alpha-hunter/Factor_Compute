import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_load import get_stock_codes_by_exchange
from src.factor_cal import StockFactorCalculator
from src.write_csv import write_csv

# ⏰ 开始计时
start_time = time.perf_counter()


#step 1: get stock list
print("step1----拉取股票列表")
stock_list_sz = get_stock_codes_by_exchange('SZ')  # 获取深圳交易所股票列表
stock_list_sh = get_stock_codes_by_exchange('SH')  # 获取上海交易所股票列表
#step 2: calculate factors
print("step2----计算因子值")
calculator_sz = StockFactorCalculator(stock_list_sz)
calculator_sh = StockFactorCalculator(stock_list_sh)
results_sz = calculator_sz.calc_all()
results_sh = calculator_sh.calc_all()


# 合并结果
all_results = {}
all_results.update(results_sz)
all_results.update(results_sh)

#step 3: write to csv
print("step3----写入CSV文件")
write_csv(all_results)



# ⏰ 结束计时
end_time = time.perf_counter()
total_time = end_time - start_time

print(f"全部完成！因子值已写入 factorValue_YF.csv 文件。")
print(f"总运行时间: {total_time:.2f} 秒")

# 可选：更详细的时间显示
if total_time >= 60:
    minutes = int(total_time // 60)
    seconds = total_time % 60
    print(f"详细时间: {minutes}分{seconds:.2f}秒")
else:
    print(f"运行时间: {total_time:.3f} 秒")