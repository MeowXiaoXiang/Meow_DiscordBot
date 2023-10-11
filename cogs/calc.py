#--------------------------Discord---------------------------------
import discord
from discord.ext import commands
#--------------------------Other-----------------------------------
import re
#------------------------------------------------------------------

class calc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.legal = re.compile(r'^[\.\de\+\-\*/% \(\)]*$')
        symbol_list = ['[\d]+e[\+\-][\d]+', '[\d\.]+', '\+', '\-', '\*', '/', '%', '\(', '\)']
        self.symbol = re.compile('(%s)' % '|'.join(symbol_list))
        
    @discord.app_commands.command(name="計算", description="簡易的四則運算")
    @discord.app_commands.describe(
        expression="輸入要計算的數學表達式，支援 + - * / ( ) 小數 科學記號e=10^"
    )
    @discord.app_commands.rename(expression="數學表達式")
    async def calc(self, interaction: discord.Interaction, expression: str):
        await interaction.response.send_message(self.Calculation(expression))
        
    def Calculation(self, expr):
        try:
            if "亞玄" in expr: # 友人要求
                return '計算結果：%s = %s' % (' '.join(expr).replace('( ', '(').replace(' )', ')').replace('+',' + ').replace('+',' + ').replace('-',' - ').replace('*',' * ').replace('/',' / '), "超級亞玄")
            self._is_easy(expr)
            self._no_exp(expr)
            self._is_calculable(expr)
            return '計算結果：%s = %s' % (self._pretty_expr(expr), str(eval(expr)).upper())
        except Exception as e:
            return str(e)
        
    def _pretty_expr(self, expr):
        result = self.symbol.findall(expr)
        return ' '.join(result).replace('( ', '(').replace(' )', ')')

    def _is_easy(self, expr):
        if self.legal.match(expr) is None:
            raise calc.NotEasyExpression()
        return True

    def _no_exp(self, expr):
        if '**' in expr:
            raise calc.ExponentNotAllowed()
        return True

    def _is_calculable(self, expr):
        try:
            exec(expr)
            return True
        except ZeroDivisionError:
            raise calc.DividByZero()
        except:
            raise calc.NotCalculable()

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
