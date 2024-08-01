#--------------------------Discord---------------------------------
import discord
from discord.ext import commands
#--------------------------Database--------------------------------
from module import connect_db, set_key, get_key
#--------------------------Type------------------------------------
from typing import Optional
#---------------------Logger and Time------------------------------
from loguru import logger
from module import TimeUtils
#---------------------------Other----------------------------------
import re
import time
import json
import requests
#------------------------------------------------------------------

class event(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.time_utils = TimeUtils()
        self.owner = self.bot.get_user(self.bot.owner_id)
        self.settings = json.load(open("setting.json", "r", encoding="utf8")) #讀取 setting.json
        self.auto_reply_message = json.load(open("auto_reply_message.json", "r", encoding="utf8")) # 讀取 auto_reply_message.json
        self.timer_auto_reply = time.time() - int(self.settings['auto_replay_cooldown'])
        self.timer_msg_emoji = time.time() - int(self.settings['emoji_record_cooldown'])
        self.timer_reaction_add = time.time() - int(self.settings['emoji_record_cooldown'])
        self.private_chat_user = None
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        self.supported_video_formats = ['.mp4', '.webm', '.mov', '.avi', '.mkv']

    @commands.Cog.listener(
    )  #若你是在main.py的話 會是bot.event 就 接收事件的 但是現在再cog內得寫成cog.listener
    async def on_message(self, msg):  #msg on_message下機器人看到的訊息
        await self.private_chat_handle(msg)
        await self.process_message(msg)
        await self.handle_mentions(msg)
        await self.process_auto_reply(msg)
        self.record_emoji_usage(msg)

    async def private_chat_handle(self, msg):
        try:
            # 若是機器人自己發的消息，直接 return
            if msg.author == self.bot.user:
                return  
            # 若頻道類型是私訊
            if msg.channel.type == discord.ChannelType.private:
                # 如果目前沒人聊天，且機器人擁有者發了訊息，得直接return掉，避免產生問題
                if self.private_chat_user is None and msg.author == self.owner:
                    return
                # 如果沒有正在聊天的，或記錄的用戶不同，則更新私聊用戶並發送首次對方用戶的資訊
                if self.private_chat_user is None or self.private_chat_user != msg.author:
                    if msg.author != self.owner:
                        self.private_chat_user = msg.author  # 更新私聊用户
                        await self.owner.send(embed=self.user_DM_information(msg.author))

                # 若不是機器人擁有者發的，那麼訊息當然是給對方的，反之如此也是
                if msg.author != self.owner:
                    attachment_links = []  # 儲存附件連結的list
                    file_attachments = []  # 儲存不支援預覽的附件
                    # 檢查所有附件url
                    for attachment in msg.attachments:
                        # 檢查附件url是否為支援的圖片或影片
                        is_supported = False
                        for format in self.supported_image_formats + self.supported_video_formats:
                            if attachment.url.endswith(format):
                                attachment_links.append(attachment.url)
                                is_supported = True
                                break  # 只增加一次附件url
                        # 若不支援預覽，則儲存附件
                        if not is_supported:
                            file_attachments.append(attachment)
                    # 發送訊息內容
                    if msg.content:
                        await self.owner.send(msg.content)
                    # 發送附件url
                    if attachment_links:
                        await self.owner.send("\n".join(attachment_links))
                    # 發送不支援預覽的附件
                    for attachment in file_attachments:
                        file_size = self.get_attachment_size(attachment.url)
                        await self.owner.send(embed=self.file_embed(msg.author, attachment, file_size))
                else:
                    attachment_links = []  # 儲存附件連結的list
                    file_attachments = []  # 儲存不支援預覽的附件
                    # 檢查所有附件url
                    for attachment in msg.attachments:
                        # 檢查附件url是否為支援的圖片或影片
                        is_supported = False
                        for format in self.supported_image_formats + self.supported_video_formats:
                            if attachment.url.endswith(format):
                                attachment_links.append(attachment.url)
                                is_supported = True
                                break  # 只增加一次附件url
                        # 若不支援預覽，則儲存附件
                        if not is_supported:
                            file_attachments.append(attachment)
                    # 發送訊息內容
                    if msg.content:
                        await self.private_chat_user.send(msg.content)
                    # 發送附件url
                    if attachment_links:
                        await self.private_chat_user.send("\n".join(attachment_links))
                    # 發送不支援預覽的附件
                    for attachment in file_attachments:
                        file_size = self.get_attachment_size(attachment.url)
                        await self.private_chat_user.send(embed=self.file_embed(msg.author, attachment, file_size))
        except Exception as e:
            logger.error(F"Error in private_chat_handle: {e}")

    def user_DM_information(self, user):
        embed = discord.Embed(title="新的私聊使用者", description=f"用戶名稱：{user.name}\n用户ID：{user.id}")
        embed.set_author(name=user.name, icon_url=user.avatar.url)
        return embed

    def get_attachment_size(self, url):
        try:
            response = requests.head(url)  # 使用 aiohttp 或 httpx 库进行异步请求
            if 'Content-Length' in response.headers:
                file_size = int(response.headers['Content-Length'])
                return file_size
            return None
        except Exception as e:
            logger.error(F"Error in get_attachment_size: {e}")

    def file_embed(self, user, attachment, file_size):
        try:
            if file_size >= 1024 * 1024:  # 大於1MB 就使用 MB 單位
                file_size_str = f"%.2f MB" % float(file_size / (1024 * 1024))
            else:
                file_size_str = f"%.2f KB" % float(file_size / 1024)
                
            embed = discord.Embed(
                title="檔案下載",
                description=F"{user.name} 向您發送了一個檔案",
            )
            embed.set_author(name=user.name, icon_url=user.avatar.url)
            embed.add_field(
                name="下載連結",
                value=f"[ :link: {attachment.filename}]({attachment.url})\n檔案大小：{file_size_str}",
                inline=False
            )
            embed.set_footer(text=F"發送時間：{self.time_utils.get_utc8_ch()}")
            return embed
        except Exception as e:
            logger.error(F"Error in file_embed: {e}")
    # ----------------------------------------------------------------

    async def process_message(self, msg):
        if msg.author != self.bot.user:
            if msg.channel.type == discord.ChannelType.private:
                self.log_private_message(msg)
            if msg.channel.type == discord.ChannelType.text:
                self.log_text_channel_message(msg)

    def log_private_message(self, msg):
        try:
            log_path = './message_log/對機器人私訊的訊息.log'
            print(F"[私訊]{self.time_utils.get_utc8_ch()}{msg.author}說：{msg.content}\n")
            with open(log_path, 'a', encoding='utf8') as fp:
                fp.write(F"{self.time_utils.get_utc8_ch()}{msg.author}說：{msg.content}\n")
        except Exception as e:
            logger.error(F"Error in log_private_message: {e}")

    def log_text_channel_message(self, msg):
        try:
            if msg.channel.id in self.settings['record_channels']:
                log_path = f'./message_log/{msg.guild}-{msg.channel}.log'
                print(F"[訊息紀錄中]{self.time_utils.get_utc8_ch()}[{msg.guild}-{msg.channel}]{msg.author}說：\n{msg.content}\n")
                with open(log_path, 'a', encoding='utf8') as fp:
                    fp.write(F"{self.time_utils.get_utc8_ch()}{msg.author}說：{msg.content}\n")
            else:
                print(F"{self.time_utils.get_utc8_ch()}[{msg.guild}-{msg.channel}]{msg.author}說:{msg.content}\n")
        except Exception as e:
            logger.error(F"Error in log_text_channel_message: {e}")

    async def handle_mentions(self, msg):
        if self.bot.user in msg.mentions:
            await msg.add_reaction(self.bot.get_emoji(int(self.settings['auto_reaction_add'])))

    async def process_auto_reply(self, msg):
        try:
            if msg.author != self.bot.user:
                for key in self.auto_reply_message.keys():
                    if key == msg.content and msg.channel.id in self.settings['auto_replay_channels']:
                        if time.time() - self.timer_auto_reply > int(self.settings['auto_replay_cooldown']):
                            self.timer_auto_reply = time.time()   
                            await msg.channel.send(self.auto_reply_message[key])
        except Exception as e:
            logger.error(F"Error in process_auto_reply: {e}")

    # 提取emoji_id的輔助函數
    def extract_emoji_id(self, target):
        try:
            return int(target.split(':')[2][:-1])
        except (IndexError, ValueError):
            return None

    # 直接使用emoji_id紀錄使用次數
    def record_emoji_usage(self, msg):
        try:
            if msg.author == self.bot.user:
                return
            
            target_list = re.findall(r"<:\w+:\d+>", msg.content)
            for target in target_list:
                emoji_id = self.extract_emoji_id(target)
                if emoji_id is not None:
                    with connect_db() as session:
                        key_value = get_key(session, emoji_id)
                        emoji_count = int(key_value) if key_value else 0
                        if time.time() - self.timer_msg_emoji > int(self.settings['emoji_record_cooldown']):
                            self.timer_msg_emoji = time.time()
                            set_key(session, emoji_id, emoji_count + 1)
                            print(F"{emoji_id} 表情 使用次數 + 1\n")
                        else:
                            set_key(session, emoji_id, 1)
                            print(F"{emoji_id} 表情 第一次使用\n")
        except Exception as e:
            logger.error(F"Error in record_emoji_usage: {e}")

    # 訊息附加emoji_id紀錄使用次數
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, pl):
        try:
            if not pl.member or pl.member.bot:
                return
            
            target_list = re.findall(r"<:\w+:\d+>", str(pl.emoji))
            for target in target_list:
                emoji_id = self.extract_emoji_id(target)
                if emoji_id is not None:
                    with connect_db() as session:
                        key_value = get_key(session, emoji_id)
                        emoji_count = int(key_value) if key_value else 0
                        if time.time() - self.timer_reaction_add > int(self.settings['emoji_record_cooldown']):
                            self.timer_reaction_add = time.time()
                            set_key(session, emoji_id, emoji_count + 1)
                            print(F"{emoji_id} 表情 使用次數 + 1 (訊息附加)\n")
                        else:
                            set_key(session, emoji_id, 1)
                            print(F"{emoji_id} 表情 第一次使用 (訊息附加)\n")
        except Exception as e:
            logger.error(F"Error in on_raw_reaction_add: {e}")

    @discord.app_commands.command(name="設定聊天對象", description="此功能僅限機器人擁有者使用，以及僅限私聊使用，用來設定聊天對象，若不輸入將會重設")
    @discord.app_commands.describe(
        user_id = "輸入用戶的id來指定聊天對象"
    )
    @discord.app_commands.rename(user_id="用戶id")
    async def private_set_userid(self, interaction: discord.Interaction, user_id: Optional[str]):
        try:
            if interaction.user == self.owner:
                if user_id:
                    user = self.bot.get_user(int(user_id))
                    if user:
                        self.private_chat_user = user # 若確認user_id是存在就存入，並顯示對方的資訊
                        await interaction.response.send_message(embed=self.user_DM_information(user), ephemeral=True)
                    else:
                        await interaction.response.send_message(embed=discord.Embed(title="錯誤", description="找不到指定的用戶", color=0xff0000), ephemeral=True)
                else:
                    self.private_chat_user = None
                    await interaction.response.send_message(embed=discord.Embed(title="聊天對象已重設", description="私訊聊天對象已經成功重設", color=0x00fff0), ephemeral=True)
            else:
                await interaction.response.send_message(embed=discord.Embed(title="權限不足", description="本指令只提供給機器人擁有者", color=0xff0000), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=discord.Embed(title="錯誤：設定用戶id時發生未知錯誤", description=F"錯誤訊息:\n{e}", color=0xff0000), ephemeral=True)
            logger.error(F"Error in private_set_userid: {e}")

async def setup(bot):
    await bot.add_cog(event(bot))
