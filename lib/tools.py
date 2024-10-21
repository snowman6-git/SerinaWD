import os, time, asyncio
from discord import ButtonStyle, Interaction, Embed, FFmpegPCMAudio

ASSET_SOUNDS = os.path.join(os.path.dirname(__file__), "..", "assets/sounds")

OPEN_SOUNDS = f"{ASSET_SOUNDS}/{"open.mp3"}"
BULLET_SOUNDS = f"{ASSET_SOUNDS}/{"bullet.mp3"}"
BANG_SOUNDS = f"{ASSET_SOUNDS}/{"bang.mp3"}"
TRIGER_SOUNDS = f"{ASSET_SOUNDS}/{"triger.mp3"}"
SPIN_SOUNDS = f"{ASSET_SOUNDS}/{"spin.mp3"}"

class SoundAsset:
    def __init__(self, bot, voice):
        self.bot = bot
        self.voice = voice
    async def play(self, sound):
        self.voice.play(FFmpegPCMAudio(source=sound))
        while self.voice.is_playing():
            await asyncio.sleep(0.5)

class Revolver: #잠 깨면 최적화 해둬라
    def __init__(self, bot, voice):
        self.bot = bot
        self.sound = SoundAsset(self.bot, voice) #나중에 고쳐

    async def reload(self, bullet):
        await self.sound.play(OPEN_SOUNDS)
        for turn in range(0, bullet): #불발탄 추가로 형평성 만들기, 채울 탄수별 속도차이넣기
            await self.sound.play(BULLET_SOUNDS)
        await self.sound.play(OPEN_SOUNDS)
        await self.sound.play(SPIN_SOUNDS)

    async def triger(self): #나중에 정리해라
        await self.sound.play(TRIGER_SOUNDS)
    async def shot(self):
        await self.sound.play(BANG_SOUNDS)    
    async def empty(self):
        await self.sound.play(OPEN_SOUNDS)


class Cogs: #잠 깨면 최적화 해둬라
    def __init__(self, bot):
        self.bot = bot
    async def load(self, target):
        try:
            await self.bot.load_extension(f"cogs.{target}")
            print(f"\033[32m{target}\033[0m is \033[32mOK\033[0m!")
            return "pass"
        except Exception as E:
            print(f"\033[31m{f"{target}"}\033[0m is \033[31mERROR\033[0m!\n{E}")
            print("="*30)
            return E
    async def reload(self, target):
        try:
            # await self.bot.reload_extension(f"cogs.{target}")
            await self.bot.unload_extension(f"cogs.{target}")
            await self.bot.load_extension(f"cogs.{target}")
            # await self.bot.tree.sync()
            print(f"\033[32m{f"{target}"}\033[0m is \033[32mreloaded!\033[0m!")
            return "pass"
        except Exception as E:
            print(f"\033[31m{f"{target}"}\033[0m is \033[31mERROR\033[0m!\n{E}")
            print("="*30)
            return E
    async def unload(self, target):
        try:
            await self.bot.unload_extension(f"cogs.{target}")
            print(f"\033[90m{f"{target}"}\033[0m is \033[90munloaded\033[0m!")
            return "pass"
        except Exception as E:
            print(f"\033[31m{f"{target}"}\033[0m is \033[31mERROR\033[0m!\n{E}")
            print("="*30)
            return E
    @staticmethod
    def find_and_load():
        return Cogs()
    
def clock(wait):
    timer = f"<t:{int(time.time()) + int(wait)}:R>" #R
    return timer


def addon_list():
    addons = []
    target = os.listdir("./cogs")
    for i in range(len(target)):
        if target[i].endswith(".py"): addons.append(target[i].split(".")[0])
    return  addons

async def bootup(bot, COGS_FOLDER):
    for filename in os.listdir(COGS_FOLDER):
        if filename.endswith(".py"):
            cogs = Cogs(bot=bot)
            await cogs.load(filename[:-3])
