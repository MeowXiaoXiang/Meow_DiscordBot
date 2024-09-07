#--------------------------Discord---------------------------------
import discord
from discord.ext import commands
#--------------------------Other-----------------------------------
import os
import json
from typing import List
#------------------------------------------------------------------

class log_viewer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = json.load(open("config/setting.json", "r", encoding="utf8")) #讀取 setting.json
        self.admin_roles = self.settings['admin_roles']

    async def log_autocomplete(self, interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice[str]]:
        logs = [logname[:-4] for logname in os.listdir('./message_log') if logname.endswith('.log')]
        return [
            discord.app_commands.Choice(name=log, value=log)
            for log in logs if current in log
        ]
    
    @discord.app_commands.command(name="下載對話日誌", description="下載對話紀錄檔案")
    @discord.app_commands.describe(
        log="選擇你要下載的對話日誌",
    )
    @discord.app_commands.rename(log = "選擇對話日誌")
    @discord.app_commands.autocomplete(log=log_autocomplete)
    async def log_download(self, interaction: discord.Interaction, log: str):
        if interaction.guild is None:
            await interaction.response.send_message(embed=discord.Embed(title="權限不足", description="本指令不支援在私訊中使用", color=0xff0000), ephemeral=True)
        elif any(role.id in self.admin_roles for role in interaction.user.roles):
            fileurl = f'message_log/{log}.log'
            if os.path.exists(fileurl):
                upfile = discord.File(fileurl)
                await interaction.response.send_message(file=upfile, ephemeral=True)
            else:
                await interaction.response.send_message(embed=discord.Embed(title="無效的檔案名稱", description="請輸入有效的檔案名稱", color=0xff0000), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(title="權限不足", description="本指令只提供給管理員", color=0xff0000), ephemeral=True)

async def setup(bot):
    await bot.add_cog(log_viewer(bot))