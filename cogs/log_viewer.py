#--------------------------Discord---------------------------------
import discord
from discord.ext import commands
#--------------------------Other-----------------------------------
import os
#------------------------------------------------------------------

class log_viewer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            admin_roles_str = os.getenv('ADMIN_ROLES', '')  # 讀取環境變數，如果不存在，則回傳空字串
            admin_roles = [int(role) for role in admin_roles_str.split(',')] if admin_roles_str else []  # 將字串分割成列表並轉換成整數
        except ValueError:
            print("環境變數 'ADMIN_ROLES' 格式不正確。")
            admin_roles = []
        self.admin_roles = admin_roles
        self.log_dir = './message_log'
        self.log_file_indices = [(index, logname) for index, logname in enumerate(os.listdir(self.log_dir)) if logname.endswith('.log')]
    
    @discord.app_commands.command(name="對話日誌清單", description="列出所有機器人攔截到的對話紀錄清單")
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def log_list(self, interaction: discord.Interaction):
        self.log_file_indices = [(index, logname) for index, logname in enumerate(os.listdir('./message_log')) if logname.endswith('.log')]
        log_list_str = ""
        for index, (_, logname) in enumerate(self.log_file_indices):
            log_list_str += F"{index}. {logname[:-4]}\n"
        description = F"下載指令：/下載對話日誌 `編號`\n```{log_list_str}```"
        embed = discord.Embed(title="對話日誌清單", description=description)
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @discord.app_commands.command(name="下載對話日誌", description="下載對話紀錄檔案")
    @discord.app_commands.describe(
        index="輸入你要下載的檔案編號 `檔案編號`",
    )
    @discord.app_commands.rename(index = "檔案編號")
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def log_download(self, interaction: discord.Interaction, index: int):
        if 0 <= index < len(self.log_file_indices):
            _, logname = self.log_file_indices[index]
            fileurl = os.path.join(self.log_dir, logname)
            if os.path.exists(fileurl):
                upfile = discord.File(fileurl)
                await interaction.response.send_message(file=upfile, ephemeral=True)
            else:
                await interaction.response.send_message(embed=discord.Embed(title="檔案不存在", description="請確認檔案是否存在", color=0xff0000), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(title="無效的編號", description="請輸入有效的編號", color=0xff0000), ephemeral=True)

async def setup(bot):
    await bot.add_cog(log_viewer(bot))