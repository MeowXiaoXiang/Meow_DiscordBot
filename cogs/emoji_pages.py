#--------------------------Discord---------------------------------
import discord
from discord.ext import commands, tasks
#--------------------------Database--------------------------------
from module import connect_db, get_all_emoji_info
#-------------------------Pagination-------------------------------
from module import Paginator
#--------------------------Other-----------------------------------
import math
#------------------------------------------------------------------

class Emoji_Pages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}  # 新增的緩存字典
        self.update_cache_task.start()
    
    def cog_unload(self):
        self.update_cache_task.cancel()  # 卸載Cog時取消定時任務。

    @tasks.loop(hours=2)
    async def update_cache_task(self):
        total = 0
        dict = {}
        conn = connect_db()
        rows = get_all_emoji_info(conn)  # 使用 get_all_emoji_info 函數來獲取所有的表情符號資訊
        for row in rows:
            key = str(row[0])
            value = str(row[1])
            if key.isdigit() and value.isdigit():
                dict[int(key)] = int(value)
                total += int(value)
        sort_data = sorted(dict.items(), key=lambda x: x[1], reverse=True)
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
        
        embed.set_footer(text=F"表情使用總計：{total_usage}")
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
            return

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

async def setup(bot):
    await bot.add_cog(Emoji_Pages(bot))