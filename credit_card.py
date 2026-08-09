import requests
import json
import os
from datetime import date, timedelta

TOKEN = os.environ.get("LINE_CHANNEL_TOKEN")

# 信用卡帳單提醒設定
CARDS = [
    {"name": "富邦",  "bill_day": 20, "due_day": 5,  "due_next_month": True},
    {"name": "聯邦",  "bill_day": 6,  "due_day": 21, "due_next_month": False},
    {"name": "國泰",  "bill_day": 17, "due_day": 2,  "due_next_month": True},
    {"name": "台新",  "bill_day": 17, "due_day": 2,  "due_next_month": True},
    {"name": "星展",  "bill_day": 1,  "due_day": 20, "due_next_month": False},
]

# 軟水系統維護設定
WATER_SOFTENER = {
    "salt": {
        "name": "🧂 軟水鹽包",
        "start_date": date(2026, 8, 22),  # 開始日期
        "interval_days": 20,              # 每20天
    },
    "pp": {
        "name": "🔵 PP濾心",
        "start_date": date(2026, 8, 22),
        "interval_months": 3,
    },
    "cto": {
        "name": "⚫ CTO活性碳濾心",
        "start_date": date(2026, 8, 22),
        "interval_months": 6,
    },
    "resin": {
        "name": "💧 樹脂",
        "start_date": date(2026, 8, 22),
        "interval_years": 3,
    }
}

# 寵物提醒設定
PET_REMINDERS = [
    {
        "name": "🐕 狗狗",
        "item": "寵愛食嗑3D",
        "day_of_month": 20,
    }
]

PAGES_URL = "https://e03436688.github.io/gopower-monitor/"

def send_line(message):
    """發送 LINE 訊息"""
    resp = requests.post(
        "https://api.line.me/v2/bot/message/broadcast",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"messages": [{"type": "text", "text": message}]}
    )
    print(f"LINE: {resp.status_code} {resp.text}")

# ===== 信用卡相關函式 =====
def get_due_date(today, card):
    """計算信用卡到期日"""
    if card["due_next_month"]:
        if today.month == 12:
            return date(today.year + 1, 1, card["due_day"])
        else:
            return date(today.year, today.month + 1, card["due_day"])
    else:
        return date(today.year, today.month, card["due_day"])

def get_bill_date(today, card):
    """計算信用卡結帳日"""
    return date(today.year, today.month, card["bill_day"])

def check_cards():
    """檢查信用卡提醒"""
    today = date.today()
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

# ===== 軟水系統相關函式 =====
def add_months(d, months):
    """增加月份（處理日期溢位）"""
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)

def check_water_softener():
    """檢查軟水系統維護提醒"""
    today = date.today()
    
    # 檢查鹽包（每12天）
    salt_config = WATER_SOFTENER["salt"]
    days_since_start = (today - salt_config["start_date"]).days
    
    if days_since_start >= 0 and days_since_start % salt_config["interval_days"] == 0:
        send_line(
            f"{salt_config['name']}提醒\n"
            f"應加入軟水系統的鹽包了\n"
            f"⏰ 下次提醒：{(today + timedelta(days=salt_config['interval_days'])).strftime('%Y/%m/%d')}"
        )
    
    # 檢查PP（每3個月）
    pp_config = WATER_SOFTENER["pp"]
    months_since = (today.year - pp_config["start_date"].year) * 12 + (today.month - pp_config["start_date"].month)
    
    if months_since >= 0 and months_since % pp_config["interval_months"] == 0 and today.day == pp_config["start_date"].day:
        next_date = add_months(today, pp_config["interval_months"])
        send_line(
            f"{pp_config['name']}提醒\n"
            f"需要更換濾心\n"
            f"⏰ 下次提醒：{next_date.strftime('%Y/%m/%d')}"
        )
    
    # 檢查CTO（每6個月）
    cto_config = WATER_SOFTENER["cto"]
    months_since = (today.year - cto_config["start_date"].year) * 12 + (today.month - cto_config["start_date"].month)
    
    if months_since >= 0 and months_since % cto_config["interval_months"] == 0 and today.day == cto_config["start_date"].day:
        next_date = add_months(today, cto_config["interval_months"])
        send_line(
            f"{cto_config['name']}提醒\n"
            f"需要更換濾心\n"
            f"⏰ 下次提醒：{next_date.strftime('%Y/%m/%d')}"
        )
    
    # 檢查樹脂（每3年）
    resin_config = WATER_SOFTENER["resin"]
    years_since = today.year - resin_config["start_date"].year
    
    if years_since >= 0 and years_since % resin_config["interval_years"] == 0 and today == resin_config["start_date"]:
        next_date = date(today.year + resin_config["interval_years"], today.month, today.day)
        send_line(
            f"{resin_config['name']}提醒\n"
            f"需要更換樹脂\n"
            f"⏰ 下次提醒：{next_date.strftime('%Y/%m/%d')}"
        )

# ===== 寵物相關函式 =====
def check_pet_reminders():
    """檢查寵物相關提醒"""
    today = date.today()
    
    for reminder in PET_REMINDERS:
        if today.day == reminder["day_of_month"]:
            send_line(
                f"{reminder['name']}餵食提醒\n"
                f"今天要餵 {reminder['item']}\n"
                f"💝 別忘了寶貝的營養！"
            )

# ===== 主函式 =====
def main():
    """執行所有提醒檢查"""
    print(f"🔔 開始檢查提醒... ({date.today()})")
    check_cards()
    check_water_softener()
    check_pet_reminders()
    print("✅ 檢查完成")

if __name__ == "__main__":
    main()
