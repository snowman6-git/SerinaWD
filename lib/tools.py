import os
import time

class Cogs:
    def __init__(self, bot):
        self.bot = bot

    # 중복코드 통합 함수
    async def load(self, target):
        return await self._manage_extension(target, "load")

    async def reload(self, target):
        return await self._manage_extension(target, "reload")

    async def unload(self, target):
        return await self._manage_extension(target, "unload")

    # 코드 통합
    async def _manage_extension(self, target, action):
        try:
            extension = f"cogs.{target}"
            if action == "load":
                await self.bot.load_extension(extension)
                print(f"\033[32m{target}\033[0m is \033[32mOK\033[0m!")
            elif action == "reload":
                await self.bot.unload_extension(extension)
                await self.bot.load_extension(extension)
                print(f"\033[32m{target}\033[0m is \033[32mreloaded!\033[0m!")
            elif action == "unload":
                await self.bot.unload_extension(extension)
                print(f"\033[90m{target}\033[0m is \033[90munloaded\033[0m!")
            return "pass"
        except Exception as E:
            # 중복 예외 처리 코드 모으기
            print(f"\033[31m{target}\033[0m is \033[31mERROR\033[0m!\n{E}")
            print("="*30)
            return E

    @staticmethod
    def find_and_load():
        return Cogs()

def clock(wait):
    return f"<t:{int(time.time()) + int(wait)}:R>"

#반복문 최적화
def addon_list():
    #TODO <- 완료 : 파일 필터링 및 변환과정 1단계로 바꾸기
    return [addon.split(".")[0] for addon in os.listdir("./cogs") if addon.endswith(".py")]

async def bootup(bot, COGS_FOLDER):
    cogs = Cogs(bot=bot)  # TODO <- 완료: cogs 클래스 인스틴스 한번만 생성후 재사용
    for filename in os.listdir(COGS_FOLDER):
        if filename.endswith(".py"):
            await cogs.load(filename[:-3])
