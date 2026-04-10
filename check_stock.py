import requests
from bs4 import BeautifulSoup
import os
import sys
import time

URL = "https://www.gopower.tw/goodsview.php?g_id=Z0278"
SOLD_OUT_TEXT = "售 完"
LINE_TOKEN = os.environ.get("LINE_CHANNEL_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

def send_line(message):
    if not LINE_TOKEN or not LINE_USER_ID:
        print("❌ 未設定 LINE 環境變數")
        return
    resp = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "to": LINE_USER_ID,
            "messages": [{"type": "text", "text": message}]
        }
    )
    if resp.status_code == 200:
        print("✅ LINE 通知已發送")
    else:
        print(f"❌ LINE 發送失敗: {resp.status_code} {resp.text}")

def check_stock():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(URL, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ 抓取失敗: {e}")
        send_line(f"⚠️ 補貨監控異常\n網頁抓取失敗，請手動確認！\n{URL}")
        sys.exit(0)

    content = resp.text
    if len(content) < 1000:
        print("⚠️ 網頁內容異常，可能沒抓到正確頁面")
        send_line(f"⚠️ 補貨監控異常\n網頁內容異常，請手動確認！\n{URL}")
        sys.exit(0)

    soup = BeautifulSoup(content, "html.parser")
    page_text = soup.get_text()

    if SOLD_OUT_TEXT not in page_text:
        print("🔴 目前仍售完")
        # 報平安由 workflow 的 schedule 另外控制
    else:
        print("🟢 售完消失！連發通知！")
        for i in range(3):
            send_line(
                f"🛒【補貨通知！第{i+1}次】\n"
                f"星展傳說對決聯名卡-終獎永恆造型\n"
                f"售完狀態已消失，請立即前往確認！\n"
                f"{URL}"
            )
            if i < 2:
                time.sleep(60)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "report":
        # 報平安模式
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            resp = requests.get(URL, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            page_text = soup.get_text()
            if SOLD_OUT_TEXT in page_text:
                send_line(f"✅ 補貨監控報平安\n目前仍售完，監控正常運作中")
            else:
                send_line(f"🛒 補貨監控報平安\n⚠️ 注意：目前偵測不到售完字樣！請確認！\n{URL}")
        except Exception as e:
            send_line(f"⚠️ 報平安失敗：{e}")
    else:
        check_stock()
