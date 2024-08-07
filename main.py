#--------------------------Discord---------------------------------
import discord
from discord.ext import commands
#--------------------------Database--------------------------------
from module import connect_db, delete_all
#---------------------Logger and Time------------------------------
from loguru import logger
from datetime import datetime
#--------------------------Type------------------------------------
from typing import List
#--------------------------Other-----------------------------------
import os
import json
#------------------------------------------------------------------
version = "v2.1.4"
start_time = datetime.now()
Imp_parm = json.load(open("setting.json", 'r', encoding='utf8')) #讀取你的setting.json
#------------------------------------------------------------------
class Meow_DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("-"), intents=discord.Intents.all())
        self.help_command = None
    #-------------當機器人準備好 會設定自己的狀態和提示已經READY!------
    async def on_ready(self):
        app_info = await self.application_info()
        self.owner_id = app_info.owner.id
        if not os.path.exists('message_log'):
            logger.info('存放訊息紀錄資料夾不存在，正在建立 message_log 資料夾...')
            os.mkdir('message_log')
            logger.info('建立成功')
        logger.info('[初始化] 設定斜線指令錯誤處理函式')
        self.tree.on_error = self.on_app_command_error
        logger.info('[初始化] 載入基本指令')
        await self.add_cog(ManagementCommand(self))
        await self.load_all_extensions()
        logger.info('[初始化] 同步斜線指令')
        await self.tree.sync()
        logger.info('[初始化] 設定機器人的狀態')
        activity = discord.Activity(type=discord.ActivityType.watching, name="喵喵喵 v2 ?") #更改這邊可以改變機器人的狀態
        await self.change_presence(activity=activity)
        self.add_view(Button_View(self))
        logger.info(F'[初始化] {self.user} | Ready!')
    #-----------------------載入 Extension -------------------------
    async def load_all_extensions(self):
        for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'cogs')):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(F'[初始化] 載入 Extension: {filename[:-3]}')
                except Exception as exc:
                    logger.error(F'[初始化] 載入 Extension 失敗: {exc}')
        logger.info('[初始化] Extension 載入完畢')
    #----------------------app_command error------------------------
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        # 斜線指令權限不足的處理
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(embed=discord.Embed(title="權限不足", description="本指令只提供給擁有[管理訊息]權限的成員使用", color=0xff0000), ephemeral=True)
        # 回報給機器人擁有者的錯誤訊息
        maintainer = self.get_user(self.owner_id)
        embed = discord.Embed(title="錯誤 Error", description=str(error))
        embed.set_author(name=F"{interaction.user.name} ({interaction.user.id})" , icon_url=interaction.user.avatar.url)
        embed.add_field(name="詳細資料 interaction data", value=interaction.data)
        if interaction.channel.type == discord.ChannelType.private:
            embed.add_field(name="頻道 Channel", value="私人 Private")
            logger.error(F"{interaction.user.name}({interaction.user.id}):{error}")
        else:
            embed.add_field(name="頻道 Channel", value=interaction.guild.name+'-'+interaction.channel.name)
            logger.error(F"{interaction.guild.name}-{interaction.channel.name}-{interaction.user.name}({interaction.user.id}):{error}")
        await maintainer.send(embed=embed)
    #---------------------on command error--------------------------
    async def on_command_error(self, ctx, error):
        logger.error(error)
        maintainer = self.get_user(self.owner_id) # 我是維護者
        embed = discord.Embed(title="錯誤 Error", description=str(error))
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.add_field(name="訊息內容 Context", value=ctx.message.content)
        if ctx.channel.type == discord.ChannelType.private:
            embed.add_field(name="頻道 Channel", value="私人 Private")
            logger.error(F"{ctx.author.name}({ctx.author.id}):{error}")
        else:
            embed.add_field(name="頻道 Channel", value=ctx.guild.name+'/'+ctx.channel.name)
            logger.error(F"{ctx.guild.name}/{ctx.channel.name}/{ctx.author.name}({ctx.author.id}):{error}")
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
                logger.info(F"已載入：{extension}")
            except commands.ExtensionAlreadyLoaded:
                await interaction.response.send_message(embed=discord.Embed(title="警告：模組已經載入", description=f"模組 `{extension}` 已經載入過，請使用重新載入或卸載", color=0xffff00), ephemeral=True)
                logger.warning(F"已經載入過：{extension}")
            except commands.ExtensionNotFound:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：模組不存在", description=f"找不到指定的模組 `{extension}`請檢查是否存在", color=0xff0000), ephemeral=True)
                logger.error(F"找不到模組：{extension}")
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：載入模組時發生未知錯誤", description=F"錯誤訊息:\n{e}", color=0xff0000), ephemeral=True)
                logger.error(F"未知錯誤：{e}")
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
                logger.info(F"已卸載：{extension}")
            except commands.ExtensionNotLoaded:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：模組尚未載入", description=f"請確認模組 `{extension}`已經載入", color=0xff0000), ephemeral=True)
                logger.error(F"尚未載入：{extension}")
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：卸載模組時發生未知錯誤", description=F"錯誤訊息:\n{e}", color=0xff0000), ephemeral=True)
                logger.error(F"未知錯誤：{e}")
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
                logger.info(F"已重新載入：{extension}")
            except commands.ExtensionNotLoaded:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：模組尚未載入", description=f"請確認模組 `{extension}`已經載入", color=0xff0000), ephemeral=True)
                logger.error(F"尚未載入：{extension}")
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="錯誤：重新載入模組時發生未知錯誤", description=F"錯誤訊息:\n{e}", color=0xff0000), ephemeral=True)
                logger.error(F"未知錯誤：{e}")
        else:
            await interaction.response.send_message(embed=discord.Embed(title="權限不足", description=F"本指令只提供給機器人擁有者", color=0xff0000), ephemeral=True)

    @discord.app_commands.command(name="機器人狀態", description="查看機器人狀態")
    async def status(self, interaction: discord.Interaction):
        embed = discord.Embed(title="目前機器人的狀態", description="以下是機器人目前的一些狀態資訊", color=discord.Color.blue())
        embed.add_field(name="目前延遲", value=f"{round(self.bot.latency*1000)}ms", inline=False)
    
        def add_field(name, values, inline=True):
            if len(values) > 0:
                for i in range(0, len(values), 10):
                    embed.add_field(name=name if i == 0 else '\u200b', value="\n".join(values[i:i+10]), inline=inline)
            else:
                embed.add_field(name=name, value="目前沒有任何資訊", inline=inline)
    
        # Add permissions
        perms = [f"- {name}" for name, value in interaction.channel.permissions_for(interaction.user) if value == True]
        add_field("機器人目前擁有的權限", perms, inline=True)
    
        # Add extensions
        all_exts = [filename[:-3] for filename in os.listdir(os.path.join(os.path.dirname(__file__), 'cogs')) if filename.endswith('.py')]
        loaded_exts = [ext.replace('cogs.', '') for ext in self.bot.extensions]
        exts = [f"- {ext} {'✅' if ext in loaded_exts else '❌'}" for ext in all_exts]
        add_field("模組狀態", exts, inline=False)
    
        # Add uptime
        embed.add_field(name="在線時間", value=f"<t:{int(start_time.timestamp())}:R>", inline=False)
    
        # Add author
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
    
        # Add footer
        embed.set_footer(text=f"目前 Discord Bot 的版本：{version}")
    
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="重設機器人資料庫", description="清除資料庫，讓機器人重新紀錄表情符號的資訊")
    async def control_menu(self, interaction: discord.Interaction):
        if interaction.user.id == self.bot.owner_id:
            await interaction.response.send_message("確定真的要清除?", view=Button_View(self.bot), ephemeral=True)
        else:
            await interaction.response.send_message('你並不是擁有者 不能使用這個指令', ephemeral=True)

class Button_View(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None) # timeout of the view must be set to None
        self.bot = bot

    def disable_buttons(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="確認", custom_id="db_del_confirm", row=0, style=discord.ButtonStyle.success, emoji="✔️") # the button has a custom_id set
    async def database_erase_confirm_callback(self, interaction, button):
        if interaction.user.id == self.bot.owner_id:
            conn = None
            try:
                conn = connect_db()
                delete_all(conn)
                self.disable_buttons()
                logger.info("清除資料庫操作完成")
                await interaction.response.edit_message(content=F"清除資料庫完成", view=self)
            except Exception as e:
                logger.error(str(e))
                self.disable_buttons()
                await interaction.response.edit_message(content=f"清除時遭遇錯誤，錯誤訊息：\n{str(e)}", view=self)
            finally:
                if conn:
                    conn.close()
        else:
            await interaction.response.send_message("您並不是機器人擁有者請勿使用此功能", ephemeral=True)

    @discord.ui.button(label="取消", custom_id="db_del_cancel", row=0, style=discord.ButtonStyle.secondary, emoji="❌") # the button has a custom_id set
    async def database_erase_cancel_callback(self, interaction, button):
        self.disable_buttons()
        logger.info("清除資料庫操作被取消")
        await interaction.response.edit_message(content="清除資料庫操作被取消", view=self)

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
        level='INFO',
        encoding='UTF-8',
        format=log_format
    )

if __name__ == '__main__':
    set_logger()
    MEOW = Meow_DiscordBot()
    try:
        MEOW.run(Imp_parm['TOKEN'])
    except Exception as e:
        logger.critical(str(e))