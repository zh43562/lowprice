import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(subject, body, attachment_file_paths):
    sender_email = os.getenv('MAIL_USERNAME')  # 发送邮箱
    receiver_email = os.getenv('MAIL_RECEIVER')  # 从 GitHub Secrets 获取接收邮箱
    smtp_server = "smtp.qq.com"
    smtp_port = 587
    password = os.getenv('MAIL_PASSWORD')  # 邮箱授权码

    # 设置邮件内容
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(body)

    for file_path in attachment_file_paths:
        part = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=file_path)
        msg.attach(part)

    # 发送邮件
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
        print(f"邮件已发送到 {receiver_email}")
    except Exception as e:
        print(f"邮件发送失败: {e}")

# 示例发送邮件
send_email(
    subject="每日股市筛选结果",
    body="请查收附件中的股市筛选结果。",
    attachment_file_paths=["lowprice_最后结果_2元超市.csv", "lowprice_最后结果_创业板.csv"]
)
