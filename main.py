#--------------------------Discord---------------------------------
import discord
from discord.ext import commands
#---------------------Logger and Time------------------------------
from loguru import logger
from datetime import datetime
#--------------------------Type------------------------------------
from typing import List
#--------------------------Other-----------------------------------
import os
import sys
import json
import traceback
#------------------------------------------------------------------
version = "v2.2"
start_time = datetime.now()
settings = json.load(open("config/setting.json", 'r', encoding='utf8')) # 讀取setting.json
#------------------------------------------------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("-"), intents=intents)
#------------------------------------------------------------------
bot.help_command = None
#-------------當機器人準備好 會設定自己的狀態和提示已經READY!----------
@bot.event
async def on_ready():
    app_info = await bot.application_info()
    bot.owner_id = app_info.owner.id
    logger.info('[初始化] 載入基本指令')
    await bot.add_cog(ManagementCommand(bot))
    await load_all_extensions()
    logger.info('[初始化] 同步斜線指令')
    slash_command = await bot.tree.sync()
    logger.info(F'[初始化] 已同步 {len(slash_command)} 個斜線指令')
    logger.info('[初始化] 設定機器人的狀態')
    activity = discord.Activity(type=discord.ActivityType.watching, name="喵喵喵 v2 ?") #更改這邊可以改變機器人的狀態
    await bot.change_presence(activity=activity)
    logger.info(F'[初始化] {bot.user} | Ready!')
#-----------------------載入 Extension -----------------------------
async def load_all_extensions():
    for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'cogs')):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(F'[初始化] 載入 Extension: {filename[:-3]}')
            except Exception as exc:
                logger.error(F'[初始化] 載入 Extension 失敗: {exc}\n{traceback.format_exc()}')
    logger.info('[初始化] Extension 載入完畢')
#----------------------app_command error---------------------------
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    # 回報給機器人擁有者的錯誤訊息
    maintainer = bot.get_user(bot.owner_id)
    embed = discord.Embed(title="斜線指令錯誤 Error", description=str(error))
    embed.set_author(name=f"{interaction.user.name} ({interaction.user.id})", icon_url=interaction.user.display_avatar.url)
    embed.add_field(name="詳細資料 interaction data", value=interaction.data)
    if interaction.channel.type == discord.ChannelType.private:
        embed.add_field(name="頻道 Channel", value="私人 Private")
        logger.error(f"{interaction.user.name}({interaction.user.id}):{error}\n{traceback.format_exc()}")
    else:
        embed.add_field(name="頻道 Channel", value=interaction.guild.name + '-' + interaction.channel.name)
        logger.error(f"{interaction.guild.name}-{interaction.channel.name}-{interaction.user.name}({interaction.user.id}):{error}\n{traceback.format_exc()}")
    await maintainer.send(embed=embed)
#----------------------on_command_error---------------------------
@bot.event
async def on_command_error(ctx, error):
    # 回報給機器人擁有者的錯誤訊息
    maintainer = bot.get_user(bot.owner_id)
    embed = discord.Embed(title="前綴指令錯誤 Error", description=str(error))
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    embed.add_field(name="訊息內容 Context", value=ctx.message.content)
    if ctx.channel.type == discord.ChannelType.private:
        embed.add_field(name="頻道 Channel", value="私人 Private")
        logger.error(f"{ctx.author.name}({ctx.author.id}):{error}\n{traceback.format_exc()}")
    else:
        embed.add_field(name="頻道 Channel", value=ctx.guild.name + '/' + ctx.channel.name)
        logger.error(f"{ctx.guild.name}/{ctx.channel.name}/{ctx.author.name}({ctx.author.id}):{error}\n{traceback.format_exc()}")
    await maintainer.send(embed=embed)

class ManagementCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def extension_autocomplete(self, interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice[str]]:
        extensions = [filename[:-3] for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'cogs')) if filename.endswith('.py')]
        return [
            discord.app_commands.Choice(name=extension, value=extension)
            for extension in extensions if current in extension
        ]
    #-----------------------COG載入重載卸載控制區-------------------------
    @discord.app_commands.command(name="載入模組", description="載入`extension`模組庫")
    @discord.app_commands.describe(extension="輸入你要載入的`extension`模組")
    @discord.app_commands.autocomplete(extension=extension_autocomplete)
    async def load(self, interaction: discord.Interaction, extension: str):
        if interaction.user.id == self.bot.owner_id:
            try:
                await self.bot.load_extension(F'cogs.{extension}')
                await interaction.response.send_message(embed=discord.Embed(title="已載入模組", description=f"`{extension}`", color=0x00ff00), ephemeral=True)
                logger.info(f"已載入：{extension}")
            except commands.ExtensionAlreadyLoaded:
                await interaction.response.send_message(embed=discord.Embed(title="警告：模組已經載入", description=f"模組 `{extension}` 已經載入過，請使用重新載入或卸載", color=0xffff00), ephemeral=True)
                logger.warning(f"已經載入過：{extension}")
            except commands.ExtensionNotFound:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：模組不存在", description=f"找不到指定的模組 `{extension}`請檢查是否存在", color=0xff0000), ephemeral=True)
                logger.error(f"找不到模組：{extension}")
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：載入模組時發生未知錯誤", description=f"錯誤訊息:\n{e}", color=0xff0000), ephemeral=True)
                logger.error(f"未知錯誤：{e}\n{traceback.format_exc()}")
        else:
            await interaction.response.send_message(embed=discord.Embed(title="權限不足", description="本指令只提供給機器人擁有者", color=0xff0000), ephemeral=True)

    @discord.app_commands.command(name="卸載模組", description="卸載`extension`模組庫")
    @discord.app_commands.describe(extension = "輸入你要卸載的`extension`模組")
    @discord.app_commands.autocomplete(extension=extension_autocomplete)
    async def unload(self, interaction: discord.Interaction, extension: str):
        if interaction.user.id == self.bot.owner_id:
            try:
                await self.bot.unload_extension(F'cogs.{extension}')
                await interaction.response.send_message(embed=discord.Embed(title="已卸載模組", description=f"`{extension}`", color=0x00ff00), ephemeral=True)
                logger.info(f"已卸載：{extension}")
            except commands.ExtensionNotLoaded:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：模組尚未載入", description=f"請確認模組 `{extension}`已經載入", color=0xff0000), ephemeral=True)
                logger.error(f"尚未載入：{extension}")
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：卸載模組時發生未知錯誤", description=f"錯誤訊息:\n{e}", color=0xff0000), ephemeral=True)
                logger.error(f"未知錯誤：{e}\n{traceback.format_exc()}")
        else:
            await interaction.response.send_message(embed=discord.Embed(title="權限不足", description="本指令只提供給機器人擁有者", color=0xff0000), ephemeral=True)

    @discord.app_commands.command(name="重新載入模組", description="重新載入`extension`模組庫")
    @discord.app_commands.describe(extension = "輸入你要重新載入的`extension`模組")
    @discord.app_commands.autocomplete(extension=extension_autocomplete)
    async def reload(self, interaction: discord.Interaction, extension: str):
        if interaction.user.id == self.bot.owner_id:
            try:
                await self.bot.reload_extension(F'cogs.{extension}')
                await interaction.response.send_message(embed=discord.Embed(title="已重新載入模組", description=f"`{extension}`", color=0x00ff00), ephemeral=True)
                logger.info(f"已重新載入：{extension}")
            except commands.ExtensionNotLoaded:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：模組尚未載入", description=f"請確認模組 `{extension}`已經載入", color=0xff0000), ephemeral=True)
                logger.error(f"尚未載入：{extension}")
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：重新載入模組時發生未知錯誤", description=f"錯誤訊息:\n{e}", color=0xff0000), ephemeral=True)
                logger.error(f"未知錯誤：{e}\n{traceback.format_exc()}")
        else:
            await interaction.response.send_message(embed=discord.Embed(title="權限不足", description=f"本指令只提供給機器人擁有者", color=0xff0000), ephemeral=True)

    @discord.app_commands.command(name="機器人狀態", description="查看機器人目前狀態")
    async def status(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        color = discord.Color.green() if latency < 100 else discord.Color.yellow() if latency < 200 else discord.Color.red()

        embed = discord.Embed(title="機器人狀態", description="目前狀態如下", color=color)
        embed.add_field(name="延遲", value=f"{latency}ms", inline=True)
        embed.add_field(name="指令數量", value=f"前綴: `{len(self.bot.commands)}`\t斜線: `{len(self.bot.tree.get_commands())}`", inline=True)
        embed.add_field(name="WebSocket", value="已連接" if not self.bot.is_ws_ratelimited() else "受限", inline=True)

        target = interaction.guild.me if interaction.guild else self.bot.user
        perms = [f"- {name}" for name, value in interaction.channel.permissions_for(target) if value]
        embed.add_field(name=f"權限（{interaction.guild.name if interaction.guild else '私訊'}）", value="\n".join(perms[:10]) or "（無）", inline=False)

        cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
        all_exts = [f[:-3] for f in os.listdir(cogs_dir) if f.endswith('.py')]
        active_exts = [e.replace("cogs.", "") for e in self.bot.extensions]
        embed.add_field(name="模組狀態", value="\n".join(f"- {e} {'✅' if e in active_exts else '❌'}" for e in all_exts), inline=False)

        embed.add_field(name="在線時間", value=f"<t:{int(start_time.timestamp())}:R>", inline=False)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Discord Bot 版本：{version}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="重啟機器人", description="重新啟動機器人")
async def restart_bot_command(interaction: discord.Interaction):
    if interaction.user.id == bot.owner_id:
        await interaction.response.send_message("您確定要重啟機器人嗎？", view=RestartView(bot, interaction), ephemeral=True)
    else:
        await interaction.response.send_message("您並不是機器人擁有者，請勿使用此功能", ephemeral=True)

class RestartView(discord.ui.View):
    def __init__(self, bot, interaction, timeout=120):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.interaction = interaction
        self.has_interacted = False  # 用來追蹤是否已經進行過互動

    def disable_buttons(self):
        for item in self.children:
            item.disabled = True

    async def on_timeout(self):
        # 當 timeout 到達時，自動禁用按鈕並更新消息
        if not self.has_interacted:
            self.disable_buttons()
            try:
                await self.interaction.edit_original_response(content="重啟操作已過期", view=self)
            except Exception as e:
                print(f"編輯消息失敗: {str(e)}")

    @discord.ui.button(label="確認", custom_id="restart_confirm", row=0, style=discord.ButtonStyle.success, emoji="✔️")
    async def restart_confirm_callback(self, interaction, button):
        if interaction.user.id == self.bot.owner_id:
            self.disable_buttons()
            self.has_interacted = True  # 設置互動標誌
            await interaction.response.edit_message(content="重啟中...", view=self)
            restart_program()
        else:
            await interaction.response.send_message("您並不是機器人擁有者，請勿使用此功能", ephemeral=True)

    @discord.ui.button(label="取消", custom_id="restart_cancel", row=0, style=discord.ButtonStyle.secondary, emoji="❌")
    async def restart_cancel_callback(self, interaction, button):
        self.disable_buttons()
        self.has_interacted = True  # 設置互動標誌
        await interaction.response.edit_message(content="重啟操作已被取消", view=self)

def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

async def on_disconnect():
    logger.info('機器人已關閉')

#---------------------------loguru設定---------------------------
def set_logger():
    log_format = (
        '{time:YYYY-MM-DD HH:mm:ss} | '
        '{level} | <{module}>:{function}:{line} | '
        '{message}'
    )
    logger.add(
        './logs/system.log',
        rotation='7 day',
        retention='30 days',
        level='WARNING',
        encoding='UTF-8',
        format=log_format
    )

if __name__ == '__main__':
    set_logger()
    try:
        bot.run(settings['TOKEN'])
    except Exception as e:
        logger.critical(str(e))