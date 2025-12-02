import efinance as ef
import pandas as pd
from datetime import date
import os

# 获取基本信息
today_str = date.today().isoformat()   # 默认格式：YYYY-MM-DD

stock_a = ef.stock.get_realtime_quotes()  # 沪深市场 A 股最新状况
stock_a['name_code'] = stock_a['股票名称'] + '_' + stock_a['股票代码'].map(str)
stock_a['name_code2'] = stock_a['市场类型'] + '_' + stock_a['股票代码'].map(str)
stock_a = stock_a[stock_a['name_code'].str.contains('ST|退_') == False]  # 删除st
file_name0 = f"lowprice_ef_1_股票_信息表_{today_str}.csv"
stock_a.to_csv(file_name0, encoding='utf_8_sig', index=False)
print('股票_信息表 Over')

# 获取沪深A股市场最新公开的股东数目变化情况 也可获取指定报告期的股东数目变化情况
df_r = ef.stock.get_latest_holder_number()
df_r['name_code'] = df_r['股票名称'] + '_' + df_r['股票代码'].map(str)
file_name1 = f"股东数目变化情况_{today_str}.csv"
df_r.to_csv(file_name1, encoding='utf_8_sig', index=False)
print('股东数目变化 Over')

# 后续筛选逻辑...

# 最终生成的 CSV 文件路径
file_name2 = f"lowprice_最后结果_2元超市_{today_str}.csv"
file_name3 = f"lowprice_最后结果_创业板_{today_str}.csv"

# 删除生成的文件
def delete_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除文件: {file_path}")

delete_files([file_name0, file_name1, file_name2, file_name3])
