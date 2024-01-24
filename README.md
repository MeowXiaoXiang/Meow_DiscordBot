# Meow_DiscordBot

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?logo=python) ![License MIT](https://img.shields.io/badge/License-MIT-green) ![Version v2.1](https://img.shields.io/badge/Version-v2.1-orange)

## 介紹

"小翔二號機" 是一個專為 Discord 伺服器 "菓之群" 所設計的 Bot。這個名稱的由來是因為我是這個 Bot 的創建者，~~所以我就是一號機。~~
~~這個 Bot 目前是運行在 replit.com 上。如果你想要在本地運行這個 Bot，請修改與 replit db 相關的程式碼，並移除 `keep_alive.py`。~~
目前已經移除`keep_alive.py`已經改成使用`sqlite3`作為資料庫在本地使用

## 安裝

在開始使用這個 Bot 之前，你需要安裝一些必要的 Python 套件。你可以使用以下的指令來安裝這些套件：

```bash
pip install -r requirements.txt
```

## 功能介紹

- `calc`：這是一個簡單的計算機功能，支援加法、減法、乘法、除法、括號運算、小數以及科學記號（e 表示 10 的次方）。
- `avatar`：這個功能可以查詢指定使用者的頭像，並且會根據頭像的顏色調整 embed 的顏色。
- `send_user`：這個功能可以讓機器人私訊指定的使用者，但前提是機器人必須已經認識該使用者。
- `send_channel`：這個功能可以讓機器人在指定的頻道發送訊息。
- `help_auto_reply_list`：這個功能可以顯示機器人的自動回應訊息清單。
- `log_list`：這個功能可以列出所有的對話紀錄。
- `log_download`：這個功能可以下載指定編號的對話紀錄檔案。

此外，機器人還會記錄在設定的頻道中的聊天紀錄，並記錄表情符號的使用情況。機器人擁有者可以透過機器人與特定的人進行聊天。

## 程式碼組件

- `pagination.py`：這是 py-cord 的部件，我簡單改寫了後讓他可以在 discord.py 使用，使用 MIT 授權。
- `time_utils.py`：這是時間相關格式化設計放置的位置。
- `database.py`：這個檔案包含了所有與資料庫相關的操作，包括建立連接、讀取和寫入資料等。

## 設定部分

- `auto_reply_message.json`：此檔案用於設定機器人的自動回應訊息。當機器人接收到特定訊息時，會根據此檔案的設定回應對應的訊息。請使用 JSON 格式來設定。
- `.env` 檔案：

  - `GUILD_ID`：請在此處填入你的伺服器 ID。
  - `ADMIN_ROLES`：請在此處填入管理員的身分組 ID，多個 ID 請使用逗號隔開。
  - `RECORD_CHANNELS`：請在此處填入你希望機器人記錄訊息的頻道 ID，多個 ID 請使用逗號隔開。
  - `AUTO_REPLAY_CHANNELS`：請在此處填入你希望機器人自動回應訊息的頻道 ID，多個 ID 請使用逗號隔開。
  - `AUTO_REPLAY_COOLDOWN`：設定機器人自動回應訊息的冷卻時間，單位為秒。
  - `EMOJI_RECORD_COOLDOWN`：設定機器人自動記錄表情使用的冷卻時間，單位為秒。
  - `AUTO_REACTION_ADD`：設定機器人受到標記時自動添加的表情，請填入表情的 ID。
  - `TOKEN`：設定機器人的Discord Bot TOKEN。