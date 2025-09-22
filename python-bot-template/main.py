# -*- coding: utf-8 -*-
"""
安全版 Telegram Bot 自動化模板
Token & 配置完全從本地讀取，保護敏感資訊。
"""

import json
import asyncio
from telegram import Bot

# --- 常數設定 ---
# 請將 '@your_channel_or_user' 換成你的目標使用者 ID 或頻道/群組的 @username
# 使用者 ID 獲取方式：可以轉發訊息給 @userinfobot
# 私人頻道/群組 ID 獲取方式：
# 1. 將 Bot 加入頻道/群組並設為管理員
# 2. 發送一則訊息到頻道/群組
# 3. 訪問 https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
# 4. 在回傳的 JSON 中找到 "chat" -> "id"，通常是一個負數
TARGET_CHAT_ID = "@your_channel_or_user"

# --- 主邏輯 ---
async def main():
    """
    主執行函數：讀取設定、初始化 Bots 並發送啟動訊息。
    """
    # === 1. 讀取本地配置 ===
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("🚨 錯誤：找不到 config.json 檔案。")
        print("請根據說明建立一個 config.json 檔案，並填入你的 Bot Token。")
        return
    except json.JSONDecodeError:
        print("🚨 錯誤：config.json 格式不正確，請檢查是否為有效的 JSON。")
        return

    if not config:
        print("🟡 警告：config.json 是空的，沒有可用的 Bot。")
        return

    print("✅ 本地設定讀取成功！")

    # === 2. 建立 Bot 物件 ===
    bots = {name: Bot(token) for name, token in config.items()}
    print(f"🤖 成功初始化 {len(bots)} 個 Bot：{', '.join(bots.keys())}")

    # === 3. 範例：非同步發送訊息 ===
    for name, bot in bots.items():
        try:
            await bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=f"🚀 {name} 已安全啟動！"
            )
            print(f"✅ {name} -> {TARGET_CHAT_ID} 訊息發送成功。")
        except Exception as e:
            print(f"❌ {name} -> {TARGET_CHAT_ID} 訊息發送失敗：{e}")
            print("   請檢查：")
            print(f"   1. Bot Token ('{name}') 是否正確。")
            print(f"   2. '{TARGET_CHAT_ID}' 是否正確，且 Bot 有權限對其發送訊息。")
            print("   3. 網路連線是否正常。")

    print("\n🎉 所有 Bot 已完成啟動程序。")

if __name__ == "__main__":
    # 使用 asyncio.run() 來執行非同步的 main 函數
    # 這在 Python 3.7+ 是標準做法
    asyncio.run(main())
