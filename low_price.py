# low_price.py (最终安全版本)

import efinance as ef
import pandas as pd
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import time

# --- 邮件发送函数 ---
def send_email(subject, body, attachment_file_paths):
    # --- 从环境变量中安全地获取所有敏感信息 ---
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    
    # 检查所有信息是否都已成功获取
    if not all([sender_email, receiver_email, password]):
        print("错误：未能获取完整的邮箱配置（发件人、收件人或密码）。")
        print("请检查 GitHub Secrets (SENDER_EMAIL, RECEIVER_EMAIL, EMAIL_PASSWORD) 是否都已正确设置。")
        return

    smtp_server = "smtp.qq.com"
    smtp_port = 587
    
    # 设置邮件内容
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # 添加附件
    for file_path in attachment_file_paths:
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
            print(f"成功附加文件: {file_path}")
        except FileNotFoundError:
            print(f"警告：找不到附件文件 {file_path}，跳过。")
            
    # 发送邮件
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
        print(f"邮件已成功发送到 {receiver_email}")
    except Exception as e:
        print(f"邮件发送失败: {e}")

# ... (脚本的其余部分，从 "文件删除函数" 到最后，都保持不变) ...

# --- 文件删除函数 ---
def delete_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除临时文件: {file_path}")

# --- 主逻辑开始 ---
print("自动化任务开始...")
today_str = date.today().isoformat()

# 1. 获取基础信息
print("正在获取 A 股最新状况...")
stock_a = ef.stock.get_realtime_quotes()
stock_a['name_code'] = stock_a['股票名称'] + '_' + stock_a['股票代码'].map(str)
stock_a['name_code2'] = stock_a['市场类型'] + '_' + stock_a['股票代码'].map(str)
stock_a = stock_a[stock_a['name_code'].str.contains('ST|退_') == False]
file_name0 = f"lowprice_ef_1_股票_信息表_{today_str}.csv"
stock_a.to_csv(file_name0, encoding='utf_8_sig', index=False)
print("股票信息表生成完毕。")

time.sleep(8)

# 2. 获取股东数目
print("正在获取股东数目变化情况...")
df_r = ef.stock.get_latest_holder_number()
df_r['name_code'] = df_r['股票名称'] + '_' + df_r['股票代码'].map(str)
file_name1 = f"股东数目变化情况_{today_str}.csv"
df_r.to_csv(file_name1, encoding='utf_8_sig', index=False)
print("股东数目变化情况表生成完毕。")

# 3. 两元超市筛选
print("开始进行“两元超市”筛选...")
df = pd.read_csv(file_name0)
df_r = pd.read_csv(file_name1)
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
filtered = df[df['最新价'] < 2].copy()
smallest_mv_index = filtered.nsmallest(200, '流通市值').index
lowest_price_index = filtered.nsmallest(200, '最新价').index
final_selection = filtered.loc[smallest_mv_index.intersection(lowest_price_index)]
df_merged = pd.merge(final_selection, df_r, on='name_code', how='left')
df_merged['量比'] = pd.to_numeric(df_merged['量比'], errors='coerce')
df_merged = df_merged[df_merged['量比'] > 0.8]
df_merged['换手率'] = pd.to_numeric(df_merged['换手率'], errors='coerce')
df_merged = df_merged[df_merged['换手率'] > 1.11]
df_merged['总市值_x'] = pd.to_numeric(df_merged['总市值_x'], errors='coerce')
df_merged = df_merged[df_merged['总市值_x'] < 20000000000]
df_final_2yuan = df_merged[['name_code2', '股票名称_x', '涨跌幅', '最新价', '最高', '最低', '今开', '涨跌额', '换手率', '量比', '动态市盈率', '成交量', '成交额', '总市值_x', '流通市值', '股东人数', '股东人数增减', '较上期变化百分比', '户均持股市值', '户均持股数量', '总市值_y']]
file_name2 = f"lowprice_最后结果_2元超市_{today_str}.csv"
df_final_2yuan.to_csv(file_name2, encoding='utf_8_sig', index=False)
print("“两元超市”筛选结果已生成。")


# 4. 创业板筛选
print("开始进行“创业板”筛选...")
df = pd.read_csv(file_name0)
df_r = pd.read_csv(file_name1)
df = df[df['name_code'].str.contains('_300|_301')]
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
filtered = df[df['最新价'] < 10].copy()
smallest_mv_index = filtered.nsmallest(200, '流通市值').index
lowest_price_index = filtered.nsmallest(200, '最新价').index
final_selection = filtered.loc[smallest_mv_index.intersection(lowest_price_index)]
df_merged = pd.merge(final_selection, df_r, on='name_code', how='left')
df_merged['量比'] = pd.to_numeric(df_merged['量比'], errors='coerce')
df_merged = df_merged[df_merged['量比'] > 1]
df_merged['换手率'] = pd.to_numeric(df_merged['换手率'], errors='coerce')
df_merged = df_merged[df_merged['换手率'] > 1.5]
df_merged['总市值_x'] = pd.to_numeric(df_merged['总市值_x'], errors='coerce')
df_merged = df_merged[(df_merged['总市值_x'] < 40000000000) & (df_merged['总市值_x'] > 2000000000)]
df_merged['成交额'] = pd.to_numeric(df_merged['成交额'], errors='coerce')
df_merged = df_merged[df_merged['成交额'] > 100000000]
df_final_cyb = df_merged[['name_code2', '股票名称_x', '涨跌幅', '最新价', '最高', '最低', '今开', '涨跌额', '换手率', '量比', '动态市盈率', '成交量', '成交额', '总市值_x', '流通市值', '股东人数', '股东人数增减', '较上期变化百分比', '户均持股市值', '户均持股数量', '总市值_y']]
file_name3 = f"lowprice_最后结果_创业板_{today_str}.csv"
df_final_cyb.to_csv(file_name3, encoding='utf_8_sig', index=False)
print("“创业板”筛选结果已生成。")

# 5. 发送邮件
print("准备发送邮件...")
files_to_send = [file_name2, file_name3]
send_email(
    subject=f"每日股市筛选结果 - {today_str}",
    body="你好，\n\n请查收附件中的今日股市筛选结果。\n\n- Gemini Business",
    attachment_file_paths=files_to_send
)

# 6. 删除生成的临时文件
print("任务完成，清理临时文件...")
delete_files([file_name0, file_name1, file_name2, file_name3])

print("自动化任务结束。")

