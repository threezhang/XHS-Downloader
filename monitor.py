import requests
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

def check_health():
    try:
        response = requests.get("http://localhost:8000/health")
        return response.status_code == 200
    except:
        return False

def send_alert(message):
    # 配置邮件发送
    sender = "your-email@example.com"
    receiver = "admin@example.com"
    password = "your-password"
    
    msg = MIMEText(message)
    msg['Subject'] = "XHS Downloader Alert"
    msg['From'] = sender
    msg['To'] = receiver
    
    try:
        with smtplib.SMTP_SSL('smtp.example.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send alert: {e}")

def main():
    while True:
        if not check_health():
            message = f"Service is down at {datetime.now()}"
            send_alert(message)
            print(message)
        time.sleep(300)  # 每5分钟检查一次

if __name__ == "__main__":
    main() 