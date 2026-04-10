import requests
import json
import os
from datetime import date, timedelta

TOKEN = os.environ.get("LINE_CHANNEL_TOKEN")

CARDS = [
    {"name": "富邦",  "bill_day": 20, "due_day": 5,  "due_next_month": True},
    {"name": "聯邦",  "bill_day": 6,  "due_day": 21, "due_next_month": False},
    {"name": "國泰",  "bill_day": 17, "due_day": 2,  "due_next_month": True},
    {"name": "台新",  "bill_day": 17, "due_day": 2,  "due_next_month": True},
    {"name": "星展",  "bill_day": 1,  "due_day": 20, "due_next_month": False},
]

PAGES_URL = "https://e03436688.github.io/gopower-monitor/"

def send_line(message):
    resp = requests.post(
        "https://api.line.me/v2/bot/message/broadcast",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"messages": [{"type": "text", "text": message}]}
    )
    print(f"LINE: {resp.status_code} {resp.text}")

def get_due_date(today, card):
    if card["due_next_month"]:
        if today.month == 12:
            return date(today.year + 1, 1, card["due_day"])
        else:
            return date(today.year, today.month + 1, card["due_day"])
    else:
        return date(today.year, today.month, card["due_day"])

def get_bill_date(today, card):
    return date(today.year, today.month, card["bill_day"])

def check_cards():
    today = date.today()
    month_key = today.strftime("%Y-%m")

    for card in CARDS:
        name = card["name"]
        bill_date = get_bill_date(today, card)
        due_date = get_due_date(today, card)

        # 帳單出來通知（結帳日後第5天）
        bill_notify_date = bill_date + timedelta(days=5)
        if today == bill_notify_date:
            send_line(
                f"💳 【{name}】帳單應已出\n"
                f"請確認金額並準備繳款\n"
                f"截止日：{due_date.strftime('%m/%d')}\n"
                f"📋 查看總覽：{PAGES_URL}"
            )

        # 截止前3天通知
        if today == due_date - timedelta(days=3):
            send_line(
                f"⚠️ 【{name}】還有3天到期！\n"
                f"截止日：{due_date.strftime('%m/%d')}\n"
                f"📋 查看總覽：{PAGES_URL}"
            )

        # 截止前1天通知
        if today == due_date - timedelta(days=1):
            send_line(
                f"🚨 【{name}】明天截止！快去繳！\n"
                f"截止日：{due_date.strftime('%m/%d')}\n"
                f"📋 查看總覽：{PAGES_URL}"
            )

if __name__ == "__main__":
    send_line("🧪 測試訊息：信用卡提醒系統連線正常！")
    check_cards()
