# Meow_DiscordBot

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?logo=python) ![License MIT](https://img.shields.io/badge/License-MIT-green) ![Version v2.2](https://img.shields.io/badge/Version-v2.2-orange)

## 介紹

"小翔二號機" 是一個專為 Discord 伺服器 "菓之群" 所設計的 Bot。這個名稱的由來是因為我是這個 Bot 的創建者，~~所以我就是一號機。~~
~~這個 Bot 目前是運行在 replit.com 上。如果你想要在本地運行這個 Bot，請修改與 replit db 相關的程式碼，並移除 `keep_alive.py`。~~
目前已經移除 `keep_alive.py`已經改成使用 `sqlite3`作為資料庫在本地使用

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
- `tic_tac_toe`: 這個功能是在 Discord 中進行井字遊戲。玩家使用表情符號進行操作，機器人會管理遊戲狀態和回合，並處理勝負判定。

此外，機器人還會記錄在設定的頻道中的聊天紀錄，並記錄表情符號的使用情況。機器人擁有者可以透過機器人與特定的人進行聊天。

## 程式碼組件

- `pagination.py`：這是來自 [Pycord](https://github.com/Pycord-Development/pycord/blob/master/discord/ext/pages/pagination.py) 的一個組件，我已經根據需求簡單修改了它，使其能夠在 Discord.py 中使用。主要的修改是移除了對 `discord.ext.bridge.BridgeContext` 的支援，因為 Discord.py 中並不存在該模組。這個修改保留了基本功能並適配了 Discord.py 的使用環境。此檔案仍然遵循 MIT 授權。
- `time_utils.py`：這是時間相關格式化設計放置的位置。
- `database.py`：這個檔案包含了所有與 SQLite 資料庫相關的操作，使用 SQLAlchemy 管理 `emoji_info` 表格的建立、讀取、寫入和刪除操作。

## 設定部分

- `auto_reply_message.json`：此檔案用於設定機器人的自動回應訊息。當機器人接收到特定訊息時，會根據此檔案的設定回應對應的訊息。請使用 JSON 格式來設定。
- `setting.json` 檔案，除了TOEKN使用字串外，其他請都使用整數：

  - `guild_id`：請在此處填入你的伺服器 ID。
  - `admin_roles`：請在此處填入管理員的身分組 ID，多個 ID 請使用逗號隔開。
  - `record_channels`：請在此處填入你希望機器人記錄訊息的頻道 ID，多個 ID 請使用逗號隔開。
  - `auto_replay_channels`：請在此處填入你希望機器人自動回應訊息的頻道 ID，多個 ID 請使用逗號隔開。
  - `auto_replay_cooldown`：設定機器人自動回應訊息的冷卻時間，單位為秒。
  - `emoji_record_cooldown`：設定機器人自動記錄表情使用的冷卻時間，單位為秒。
  - `auto_reaction_add`：設定機器人受到標記時自動添加的表情，請填入表情的 ID。
  - `TOKEN`：設定機器人的 Discord Bot TOKEN。