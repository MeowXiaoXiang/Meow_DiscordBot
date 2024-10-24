# emoji_pages.py
#--------------------------Discord---------------------------------
import discord
from discord.ext import commands, tasks
#-------------------Database and Pagination------------------------
from module import Paginator, connect_db, delete_all, get_all_emoji_info
#--------------------------Other-----------------------------------
import math
import traceback
from loguru import logger
#------------------------------------------------------------------

class Emoji_Pages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}  # 新增的緩存字典
        self.update_cache_task.start()
    
    def cog_unload(self):
        self.update_cache_task.cancel()  # 卸載Cog時取消定時任務

    @tasks.loop(hours=1)
    async def update_cache_task(self):
        total = 0
        emoji_dict = {}
        with connect_db() as session:
            rows = get_all_emoji_info(session)  # 使用 get_all_emoji_info 函數來獲取所有的表情符號資訊
            for row in rows:
                key = int(row[0])
                value = int(row[1])
                emoji_dict[key] = value
                total += value
        sort_data = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)
        self.cache['emoji_data'] = sort_data, total

    def get_emoji_data(self):
        return self.cache.get('emoji_data', ([], 0))

    def gen_page(self, page=1):
        embed = discord.Embed(title="表情符號的使用率統計", color=0xccab2b)
        items_per_page = 25
        start_index = (page - 1) * items_per_page
        end_index = min(len(self.get_emoji_data()[0]), page * items_per_page)
        
        emoji_data = self.get_emoji_data()[0]
        total_usage = self.get_emoji_data()[1]
        
        for i in range(start_index, end_index):
            emoji_id, usage_count = emoji_data[i]
            emoji = self.bot.get_emoji(emoji_id)
            usage_percentage = (usage_count / total_usage) * 100
            
            field_value = '{:.2f}% (使用次數：{})'.format(usage_percentage, usage_count)
            embed.add_field(name=emoji, value=field_value, inline=True)
        
        embed.set_footer(text=f"表情使用總計：{total_usage}")
        return embed
    
    @discord.app_commands.command(name="表情符號統計資料", description="查看這個伺服器表情符號統計資料")
    async def emoji_status(self, interaction: discord.Interaction):
        if 'emoji_data' not in self.cache or not self.get_emoji_data()[0]:  # 如果緩存中沒有 'emoji_data' 鍵，或者 'emoji_data' 是空的
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="表情統計錯誤",
                    description="錯誤訊息:\n目前是空的，可能資料尚未更新\n請稍後再試",
                    color=0xff0000
                ),
                ephemeral=True
            )
            return  # 提前返回，不執行後面的程式碼

        try:
            emoji_data = [self.gen_page(i) for i in range(1, math.ceil(len(self.get_emoji_data()[0])/25)+1)]
            paginator = Paginator(pages=emoji_data)
            await paginator.respond(interaction, ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="表情統計錯誤",
                    description=f"錯誤訊息:\n{e}",
                    color=0xff0000
                ),
                ephemeral=True
            )
            logger.error(f"表情統計錯誤:{e}\n{traceback.format_exc()}")

    @discord.app_commands.command(name="重設機器人資料庫", description="清除資料庫，讓機器人重新紀錄表情符號的資訊")
    async def control_menu(self, interaction: discord.Interaction):
        if interaction.user.id == self.bot.owner_id:
            await interaction.response.send_message("確定真的要清除?", view=Button_View(self.bot, interaction))
        else:
            await interaction.response.send_message('你並不是擁有者 不能使用這個指令', ephemeral=True)

class Button_View(discord.ui.View):
    def __init__(self, bot, interaction, timeout=120):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.interaction = interaction  # 保存 interaction
        self.has_interacted = False  # 用來追踪是否已經進行過互動

    def disable_buttons(self):
        for item in self.children:
            item.disabled = True

    async def on_timeout(self):
        # 當 timeout 到達時，自動禁用按鈕並更新消息
        if not self.has_interacted:
            self.disable_buttons()
            try:
                # 使用保存的 interaction 來編輯消息
                await self.interaction.edit_original_response(content="清除資料庫操作已過期", view=self)
            except Exception as e:
                logger.error(f"編輯消息失敗: {str(e)}")

    @discord.ui.button(label="確認", custom_id="db_del_confirm", row=0, style=discord.ButtonStyle.success, emoji="✔️")
    async def database_erase_confirm_callback(self, interaction, button):
        if interaction.user.id == self.bot.owner_id:
            try:
                with connect_db() as session:
                    delete_all(session)
                    self.disable_buttons()
                    self.has_interacted = True  # 設置互動標誌
                    logger.info("清除資料庫操作完成")
                    await interaction.response.edit_message(content="清除資料庫完成", view=self)
            except Exception as e:
                logger.error(str(e))
                self.disable_buttons()
                await interaction.response.edit_message(content=f"清除時遭遇錯誤，錯誤訊息：\n{str(e)}", view=self)
        else:
            await interaction.response.send_message("您並不是機器人擁有者請勿使用此功能", ephemeral=True)

    @discord.ui.button(label="取消", custom_id="db_del_cancel", row=0, style=discord.ButtonStyle.secondary, emoji="❌")
    async def database_erase_cancel_callback(self, interaction, button):
        self.disable_buttons()
        self.has_interacted = True  # 設置互動標誌
        logger.info("清除資料庫操作被取消")
        await interaction.response.edit_message(content="清除資料庫操作被取消", view=self)

async def setup(bot):
    await bot.add_cog(Emoji_Pages(bot))