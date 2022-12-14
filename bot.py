from discord.ext import commands
from discord import Intents
import sys
import os
import glob

token = ""

os.chdir(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(1, os.getcwd())


os_slash = "\\" if sys.platform == "win32" else "/"

default_intents = Intents.default()
default_intents.members = True
default_intents.typing = False
default_intents.presences = True

class Bot(commands.Bot):
    def __init__(self):
        self.prefix = "//"
        super().__init__(command_prefix=self.prefix, intents=default_intents, reconnect=True)

    def start_bot(self, token):
        print("Préparation des cogs")
        self.load_commands()
        print("Lancement de l'application")
        self.run(token)

    async def on_ready(self):
        print("Bot prêt")

    def load_commands(self):
        cogs_file = glob.iglob(f"cogs{os_slash}**.py")
        for files in cogs_file:
            files = files.split(f"{os_slash}")[1][:-3]
            print(f"Lancement du module {files}")
            self.load_extension(f'cogs.{files}')

bot = Bot()
bot.start_bot(token)
