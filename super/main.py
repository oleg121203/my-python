import os
import discord
from discord.ext import commands
from spor import спор, answers, models, questions

if __name__ == '__main__':
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    TOKEN_FILE = os.path.join(PROJECT_DIR, 'token.txt')

    try:
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print(f"Помилка: Файл {TOKEN_FILE} не знайдено")
        exit(1)

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.typing = False
    intents.presences = False

    class Bot(commands.Bot):
        def __init__(self):
            super().__init__(command_prefix='/', intents=intents)

        async def setup_hook(self):
            await self.add_cog(Model1(self))

        async def on_ready(self):
            print(f"Бот запущено! Ім'я користувача: {self.user.name}")

    class Model1(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        def read_questions(self, file_name):
            try:
                with open(file_name, 'r') as f:
                    return [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                return []

        @commands.command(name='програма')
        async def програма(self, ctx, *, аргументи: str):
            try:
                if ':' not in аргументи:
                    await ctx.send("Використання: /програма <тема>:<модель1>,<модель2>")
                    return

                тема, моделі_строка = аргументи.split(':', 1)
                моделі = [м.strip() for м in моделі_строка.split(',')]
                
                if not моделі:
                    await ctx.send("Потрібно вказати хоча б одну модель")
                    return

                questions_file = os.path.join(PROJECT_DIR, 'src', 'questions.txt')
                питання = self.read_questions(questions_file)
                
                if not питання:
                    await ctx.send("Не вдалося знайти питання у файлі")
                    return

                відповідь = f"Тема: {тема}\nМоделі: {', '.join(моделі)}\n\nПитання:\n"
                відповідь += '\n'.join(f"{i+1}. {q}" for i, q in enumerate(питання))
                
                await ctx.send(відповідь)

            except Exception as e:
                await ctx.send(f"Помилка: {str(e)}")

        @commands.command(name='спор')
        async def спор_command(self, ctx, *, промт: str):
            await спор(ctx, промт)

    bot = Bot()

    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("Помилка: Неправильний токен. Перевірте файл token.txt")
    except Exception as e:
        print(f"Помилка: {e}")
