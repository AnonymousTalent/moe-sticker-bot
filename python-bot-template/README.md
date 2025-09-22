# 安全版 Telegram Bot 自動化 Python 模板

這是一個安全、可擴展的 Python 模板，用於快速啟動 Telegram 機器人，並將敏感的 Token 資訊安全地存放在本地。

此模板專為在 Termux、Pydroid 3 或任何標準 Python 環境中執行而設計。

## ✨ 功能亮點

- **安全**：Bot Token 等敏感設定儲存在本地 `config.json`，並已加入根目錄的 `.gitignore`，避免外洩到公開倉庫。
- **可擴展**：輕鬆在 `config.json` 中新增或移除機器人，無需修改程式碼。
- **非同步**：使用 `asyncio` 進行非同步操作，效能更佳，適合處理多個機器人或高負載任務。
- **易於部署**：包含 `requirements.txt`，一鍵安裝所有依賴。

## 🚀 快速啟動

請依照以下步驟來設定並執行你的機器人：

### 1. 複製並設定 `config.json`

本目錄提供了一個範例設定檔 `config.json.example`。請先將其複製一份並命名為 `config.json`。

```bash
cp config.json.example config.json
```

然後，編輯 `config.json`，將其中的 placeholder token 換成你自己的真實 Bot Token。

```json
{
    "StormHawk_bot": "8337263103:AAGIUzrl9pb2rnviTCR7MZxDtJErSdJw0AY",
    "StormMedic_bot": "8485555463:AAGnou_FJyvlSsmMTOgCBpcFMcuhtBo2m2Y"
}
```

### 2. 安裝依賴套件

建議在虛擬環境中安裝。

```bash
# 建立虛擬環境 (可選，但建議)
python -m venv .venv
source .venv/bin/activate  # 在 Windows 上是 `.venv\Scripts\activate`

# 安裝依賴
pip install -r requirements.txt
```

### 3. 修改發送目標

打開 `main.py`，找到 `TARGET_CHAT_ID` 這個變數，將其值從 `'@your_channel_or_user'` 改成你希望機器人發送訊息的目標頻道 ID 或使用者 ID。

```python
# 請將 '@your_channel_or_user' 換成你的目標
TARGET_CHAT_ID = "@your_channel_or_user"
```
檔案內有關於如何獲取 ID 的詳細說明。

### 4. 執行！

一切就緒後，執行主程式：

```bash
python main.py
```

如果設定正確，你將在終端機看到啟動成功的訊息，並且指定的頻道或使用者會收到來自所有 Bot 的啟動通知。

## 🔧 未來擴展

你可以基於此模板進行擴展，例如：
- 增加新的自動化指令。
- 整合資料庫進行數據儲存。
- 連接其他 API 實現更複雜的功能。
