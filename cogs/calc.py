#--------------------------Discord---------------------------------
import discord
from discord.ext import commands
#--------------------------Other-----------------------------------
import re
#------------------------------------------------------------------

class calc(commands.Cog):
    LEGAL = re.compile(r'^[\.\de\+\-\*/% \(\)]*$')
    SYMBOL = re.compile('(%s)' % '|'.join(['[\d]+e[\+\-][\d]+', '[\d\.]+', '\+', '\-', '\*', '/', '%', '\(', '\)']))

    def __init__(self, bot):
        self.bot = bot 

    @commands.command(name='calc', aliases=['計算機' , '計算'], brief="簡易的四則運算", description=f"簡易的四則運算(支援: + - * / ( ) 小數 科學記號e=10^)\n中間不能有空格 不支援指數運算\n使用方法：-calc [數學算式]")
    async def calc_c(self,ctx, *args):
        msg = self.calculate(' '.join(args))
        await ctx.send(msg)

    @discord.app_commands.command(name="計算", description="簡易的四則運算")
    @discord.app_commands.describe(
        expression="輸入要計算的數學表達式，支援 + - * / ( ) 小數 科學記號e=10^"
    )
    @discord.app_commands.rename(expression="數學表達式")
    async def calc(self, interaction: discord.Interaction, expression: str):
        await interaction.response.send_message(self.calculate(expression))

    def calculate(self, expr):
        if "亞玄" in expr: # 友人要求
            return '計算結果：%s = %s' % (expr, "超級亞玄".upper())
        self.check_expression(expr)
        result = self.evaluate_expression(expr)
        return self.format_result(expr, result)

    def check_expression(self, expr):
        if self.LEGAL.match(expr) is None:
            raise self.NotEasyExpression()
        if '**' in expr:
            raise self.ExponentNotAllowed()
        try:
            exec(expr)
        except ZeroDivisionError:
            raise self.DividByZero()
        except:
            raise self.NotCalculable()

    def evaluate_expression(self, expr):
        result = eval(expr)
        if isinstance(result, float):
            result = round(result, 3)
        return result

    def format_result(self, expr, result):
        pretty_expr = ' '.join(self.SYMBOL.findall(expr)).replace('( ', '(').replace(' )', ')')
        return '計算結果：%s = %s' % (pretty_expr, str(result).upper())

    class NotEasyExpression(Exception):
        def __str__(self):
            return '只能包含數字和 + - * / % e'

    class ExponentNotAllowed(Exception):
        def __str__(self):
            return '不允許指數運算！'

    class NotCalculable(Exception):
        def __str__(self):
            return '運算式格式錯誤'

    class DividByZero(Exception):
        def __str__(self):
            return '算式出現除以零的錯誤'

async def setup(bot):
    await bot.add_cog(calc(bot))