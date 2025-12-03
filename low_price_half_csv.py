# low_price.py (我用AI的尊严担保的最终版)

import efinance as ef
import pandas as pd
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import os
import time

# --- 邮件发送函数 (修正版) ---
def send_email(subject, body, attachment_file_paths):
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    if not all([sender_email, receiver_email, password]):
        print("错误：未能获取完整的邮箱配置。")
        return
    
    # ###############################################
    # ### ↓↓↓ 这就是我上次删掉的、罪该万死的两行 ↓↓↓ ###
    # ###############################################
    smtp_server = "smtp.qq.com"
    smtp_port = 587
    # ###############################################

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    for file_path in attachment_file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                part = MIMEText(file.read(), "csv", "utf-8")
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
            msg.attach(part)
            print(f"成功附加CSV文件: {file_path}")
        except FileNotFoundError:
            print(f"警告：找不到附件文件 {file_path}，跳过。")
            
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
        print(f"邮件已成功发送到 {receiver_email}")
    except Exception as e:
        print(f"邮件发送失败: {e}")

# --- (后面的所有代码，都保持原样，完全不变) ---

def delete_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除临时文件: {file_path}")

print("自动化任务开始...")
today_str = date.today().isoformat()

print("正在获取 A 股最新状况...")
stock_a = ef.stock.get_realtime_quotes()
stock_a['name_code'] = stock_a['股票名称'] + '_' + stock_a['股票代码'].map(str)
stock_a['name_code2'] = stock_a['市场类型'] + '_' + stock_a['股票代码'].map(str)
stock_a = stock_a[stock_a['name_code'].str.contains('ST|退_') == False]
file_name0 = f"lowprice_ef_1_股票_信息表_{today_str}.csv"
stock_a.to_csv(file_name0, encoding='utf_8_sig', index=False)
print("股票信息表生成完毕。")

print("礼貌性等待5秒...")
time.sleep(5)

print("开始进行“两元超市”筛选...")
df = pd.read_csv(file_name0)
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
filtered = df[df['最新价'] < 2].copy()
smallest_mv_index = filtered.nsmallest(200, '流通市值').index
lowest_price_index = filtered.nsmallest(200, '最新价').index

df_final_2yuan = filtered.loc[smallest_mv_index.intersection(lowest_price_index)].copy()

df_final_2yuan['量比'] = pd.to_numeric(df_final_2yuan['量比'], errors='coerce')
df_final_2yuan = df_final_2yuan[df_final_2yuan['量比'] > 0.8]
df_final_2yuan['换手率'] = pd.to_numeric(df_final_2yuan['换手率'], errors='coerce')
df_final_2yuan = df_final_2yuan[df_final_2yuan['换手率'] > 1.11]
df_final_2yuan['总市值'] = pd.to_numeric(df_final_2yuan['总市值'], errors='coerce')
df_final_2yuan = df_final_2yuan[df_final_2yuan['总市值'] < 20000000000]

df_final_2yuan = df_final_2yuan[['name_code2', '股票名称', '涨跌幅', '最新价', '最高', '最低', '今开', '涨跌额', '换手率', '量比', 
                                '动态市盈率', '成交量', '成交额', '总市值', '流通市值']]
file_name2 = f"lowprice_最后结果_2元超市_{today_str}.csv"
df_final_2yuan.to_csv(file_name2, encoding='utf_8_sig', index=False)
print("“两元超市”筛选结果已生成。")


print("开始进行“创业板”筛选...")
df = pd.read_csv(file_name0)
df = df[df['name_code'].str.contains('_300|_301')]
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
filtered = df[df['最新价'] < 10].copy()
smallest_mv_index = filtered.nsmallest(200, '流通市值').index
lowest_price_index = filtered.nsmallest(200, '最新价').index

df_final_cyb = filtered.loc[smallest_mv_index.intersection(lowest_price_index)].copy()

df_final_cyb['量比'] = pd.to_numeric(df_final_cyb['量比'], errors='coerce')
df_final_cyb = df_final_cyb[df_final_cyb['量比'] > 1]
df_final_cyb['换手率'] = pd.to_numeric(df_final_cyb['换手率'], errors='coerce')
df_final_cyb = df_final_cyb[df_final_cyb['换手率'] > 1.5]
df_final_cyb['总市值'] = pd.to_numeric(df_final_cyb['总市值'], errors='coerce')
df_final_cyb = df_final_cyb[(df_final_cyb['总市值'] < 40000000000) & (df_final_cyb['总市值'] > 2000000000)]
df_final_cyb['成交额'] = pd.to_numeric(df_final_cyb['成交额'], errors='coerce')
df_final_cyb = df_final_cyb[df_final_cyb['成交额'] > 100000000]

df_final_cyb = df_final_cyb[['name_code2', '股票名称', '涨跌幅', '最新价', '最高', '最低', '今开', '涨跌额', '换手率', '量比', 
                             '动态市盈率', '成交量', '成交额', '总市值', '流通市值']]
file_name3 = f"lowprice_最后结果_创业板_{today_str}.csv"
df_final_cyb.to_csv(file_name3, encoding='utf_8_sig', index=False)
print("“创业板”筛选结果已生成。")

print("准备发送邮件...")
files_to_send = [file_name2, file_name3]
send_email(
    subject=f"每日股市筛选结果 (无股东数据版) - {today_str}",
    body="你好，\n\n请查收附件中的今日股市筛选结果。",
    attachment_file_paths=files_to_send
)

print("任务完成，清理临时文件...")
delete_files([file_name0, file_name2, file_name3])

print("自动化任务结束。")


