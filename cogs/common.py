#--------------------------Discord---------------------------------
import discord
from discord.ext import commands
#--------------------------module----------------------------------
from module import TimeUtils, Paginator
#--------------------------Type------------------------------------
from typing import Optional, Union
#--------------------------Other-----------------------------------
import re
import math
import json
import requests
import traceback
from PIL import Image
from io import BytesIO
from loguru import logger
#------------------------------------------------------------------

class Common(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_reply_data = json.load(open("config/auto_reply_message.json", "r", encoding="utf8")) # 讀取 auto_reply_message.json
        self.log_path = './message_log/使用機器人發送的訊息.log'

    @discord.app_commands.command(name="查看成員頭貼", description="顯示目標成員的頭貼，可擇一使用選擇用戶或輸入用戶id")
    @discord.app_commands.describe(
        member = "選擇你想查看的成員",
        user_id = "輸入用戶id"
    )
    @discord.app_commands.rename(member="成員", user_id="用戶id")
    async def avatar(self, interaction: discord.Interaction, member: Optional[Union[discord.Member, discord.User]] = None, user_id: Optional[str] = None):
        if not member and not user_id:
            member = interaction.user

        if member and user_id:
            await interaction.response.send_message(embed=discord.Embed(title="錯誤", description="請勿同時輸入成員和用戶id", color=0xff0000), ephemeral=True)
            return

        if user_id:
            try:
                user_id_int = int(user_id)
                user = self.bot.get_user(user_id_int)
                if user is None:
                    await interaction.response.send_message(embed=discord.Embed(
                        title="錯誤", 
                        description="無法找到指定的用戶", 
                        color=0xff0000
                        ), 
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.response.send_message(embed=discord.Embed(
                        title="錯誤",
                        description="請輸入正確的用戶id\n可透過打開discord設定內的開發者模式，使用滑鼠右鍵選單來對用戶複製id",
                        color=0xff0000
                    ),
                    ephemeral=True
                )
                return

        if member:
            member = member
        elif user_id:
            member = user

        avatar_url = member.avatar.url
        response = requests.get(avatar_url)
        image = Image.open(BytesIO(response.content))
        image = image.convert("RGB")
        pixels = image.getdata()
        r_avg = 0
        g_avg = 0
        b_avg = 0
        for pixel in pixels:
            r, g, b = pixel
            r_avg += r
            g_avg += g
            b_avg += b
        num_pixels = image.size[0] * image.size[1]
        r_avg //= num_pixels
        g_avg //= num_pixels
        b_avg //= num_pixels
        avg_color = (r_avg, g_avg, b_avg)
        color = discord.Color.from_rgb(*avg_color)
        embed = discord.Embed(title=F"{member.name} 的頭貼", description=F"[ :link: [完整大圖連結]]({avatar_url})\n", color=color)
        embed.set_image(url=avatar_url)
        await interaction.response.send_message(embed=embed)


    @discord.app_commands.command(name="讓機器人朝用戶發送訊息", description="這功能可以讓你以機器人的名義來發送訊息給目標使用者")
    @discord.app_commands.describe(
        user_id = "輸入你要私訊的使用者ID (可以去Discord內的設定→進階內把[開發者模式]打開，然後對使用者的名子用滑鼠右鍵複製使用者ID)",
        message = "輸入你想私訊給目標使用者的訊息"
    )
    @discord.app_commands.rename(user_id="使用者的id", message="訊息")
    async def send_user(self, interaction: discord.Interaction, user_id:str, message:str):
        try:
            user = self.bot.get_user(int(user_id))
            await user.send(message)
            with open(self.log_path, 'a', encoding='utf8') as fp:
                fp.write(F"{TimeUtils.get_utc8_ch()}{interaction.user}用機器人對使用者[{user.name}]說：{message}\n")
            await interaction.response.send_message(F"機器人已發送訊息給 [{user.name}]", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="機器人朝頻道發送訊息產生錯誤",
                    description=f"錯誤訊息:{e}",
                    color=0xff0000
                ), ephemeral=True
            )
            logger.error(f"機器人朝頻道發送訊息產生錯誤:{e}\n{traceback.format_exc()}")

    @discord.app_commands.command(name="讓機器人朝頻道發送訊息", description="這功能可以讓你以機器人的名義來發送訊息到頻道")
    @discord.app_commands.describe(
        channel = "選擇你要發送訊息的頻道",
        message = "輸入你想發送給頻道的訊息"
    )
    @discord.app_commands.rename(channel="頻道", message="訊息")
    async def send_channel(self, interaction: discord.Interaction, channel: discord.TextChannel, message:str):
        try:
            await channel.send(message)
            with open(self.log_path, 'a', encoding='utf8') as fp:
                fp.write(f"{TimeUtils.get_utc8_ch()}{interaction.user}用機器人對頻道 [{channel.name}] 說：{message}\n")
            await interaction.response.send_message(F"機器人已發送訊息到 [{channel.name}]", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=F"機器人朝頻道 [{channel.name}] 發送訊息產生錯誤",
                    description=F"錯誤訊息:{e}",
                    color=0xff0000
                ), ephemeral=True
            )
    
    def gen_auto_reply_list(self):
        pages = []
        items_per_page = 15
        total_items = len(self.auto_reply_data)
        total_pages = math.ceil(total_items / items_per_page)
        
        keys = list(self.auto_reply_data.keys())  # 取得所有的 key
        
        for page_number in range(total_pages):
            embed = discord.Embed(title="機器人會自動回應訊息的清單", color=0xccab2b)
            start_index = page_number * items_per_page
            end_index = min(start_index + items_per_page, total_items)
            
            for i in range(start_index, end_index):
                target = keys[i]  # 使用索引來取得 key
                response = self.auto_reply_data[target]  # 使用 key 取得 value
                if re.match(r"(http|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?", response):
                    response = F"[  :link: GIF或圖片]({response})"
                embed.add_field(name=target, value=response, inline=True)
            embed.set_footer(text="訊息帶有15秒冷卻時間")
            pages.append(embed)
        
        return pages

    @discord.app_commands.command(name="自動回覆訊息清單", description="機器人自動回應訊息的清單")
    async def help_auto_reply_list(self, interaction: discord.Interaction):
        try:
            paginator = Paginator(pages=self.gen_auto_reply_list())
            await paginator.respond(interaction, ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="自動回覆訊息清單錯誤",
                    description=f"錯誤訊息:\n{e}",
                    color=0xff0000
                ),
                ephemeral=True
            )
            logger.error(f"自動回覆訊息清單錯誤:{e}\n{traceback.format_exc()}")

async def setup(bot):
    await bot.add_cog(Common(bot))