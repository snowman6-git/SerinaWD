from discord.ext import commands
from discord import app_commands
import discord, asyncio, time
from discord import ButtonStyle, Interaction, Embed, FFmpegPCMAudio, VoiceClient
from discord.ui import View, Button
from discord.ext.commands import Bot
from lib.tools import clock
import os

ASSET_SOUNDS = os.path.join(os.path.dirname(__file__), "..", "assets/sounds")
def asset_reload(DView, sounds):
    for i in range(len(sounds)): #사운드 리스트에서 하나씩 리턴함
        button = discord.ui.Button(style=discord.ButtonStyle.gray, label=f"{i+1}: {sounds[i]}", custom_id=str(i))#, emoji=bt_list[i])
        try: DView.add_item(button)
        except ValueError:
            print("밸류 에러")
    return DView

#시간 함수
def clock(hours=0, minutes=0, seconds=0):
    total_seconds = (hours * 3600) + (minutes * 60) + seconds
    return f"<t:{int(time.time()) + total_seconds}:R>"

async def voice_connect(self, interaction): #나중에 모듈화 해서 글로벌 하게 사용하기
    voice: VoiceClient = None
    connection: VoiceClient
    for connection in self.bot.voice_connections: #voice_connections run.py 메인
        if connection.channel.id == interaction.user.voice.channel.id:
            voice = connection
            break
    if voice == None:
        old_connection = interaction.guild.voice_client
        if old_connection != None:
            await old_connection.disconnect()
            self.bot.voice_connections.remove(old_connection)
        voice = await interaction.user.voice.channel.connect()
        self.bot.voice_connections.append(voice)
        
    return voice

class Game(commands.Cog,):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        # print(f'{self.bot.user}의 슬래시 커맨드가 동기화되었습니다.')
    
    #TODO <- 완료: 타이머 고치기
    @app_commands.command(name="타이머", description="시간 포메팅")
    @app_commands.describe(hours="시간", minutes="분", seconds="초")
    async def timer(self, interaction: discord.Interaction, hours: int = 0, minutes: int = 0, seconds: int = 0):
        try:
            timer_result = clock(hours, minutes, seconds) #입력값을 받고 타이머 값으로 설정
            await interaction.response.defer()

            await interaction.followup.send(content=f"타이머 설정 완료: {timer_result}") #타이머값 설정
        except Exception as E:
            await interaction.followup.send(content=f"에러: {str(E)}")

    @commands.command("사운드")#사운드나 패키지로 함수 하나로 수정해놔라. ex(asset_play)
    async def upload(self, ctx: commands.Context):
        channel = self.bot.get_channel(1075726581642838096)
        embed = Embed(title=f"사운드에셋: 로딩중", description=f"")
        menu = await channel.send(embed=embed)
        
        self.sounds = os.listdir(ASSET_SOUNDS)
        page_len = (len(self.sounds) // 25) + 1
        for i in range(page_len):
            view = View(timeout=9e9**2)
            if i == 0:
                refresh_btn = Button(
                    style=ButtonStyle.primary,
                    label="새로고침",
                    custom_id="refresh"
                )
                refresh_btn.callback = self.upload
                view.add_item(refresh_btn)

            start = i * 25
            end = (i + 1) * 25
            if i == 0:
                end -= len(view.children)

            sound_frag = self.sounds[start:end]
            for ii, sound in enumerate(sound_frag): #사운드 리스트에서 하나씩 리턴함
                index = str((i * 25) + ii)
                button = Button(style=ButtonStyle.gray, label=f"{index}: {sound}", custom_id=index)
                button.callback = self._on_button_click
                view.add_item(button)

            embed = Embed(title=f"로드: {len(self.sounds)}개", description=f"")
            await menu.edit(embed=embed, view=view)

    async def _on_button_click(self, interaction: Interaction):
        await interaction.response.defer()
        try:
            voice: VoiceClient = None
            connection: VoiceClient
            for connection in self.bot.voice_connections: #voice_connections run.py 메인
                if connection.channel.id == interaction.user.voice.channel.id:
                    voice = connection
                    break

            if voice == None:
                old_connection = interaction.guild.voice_client
                if old_connection != None:
                    await old_connection.disconnect()
                    self.bot.voice_connections.remove(old_connection)

                voice = await interaction.user.voice.channel.connect()
                self.bot.voice_connections.append(voice)

            key = interaction.data["custom_id"]
            
            if key.isdigit():
                if voice.is_playing(): voice.stop()
                audio_name = self.sounds[int(key)]
                audio = FFmpegPCMAudio(source=f"{ASSET_SOUNDS}/{audio_name}")
                voice.play(audio)
        except Exception as E:
            print(E)

    async def timeout_button(self, view, button, message, timeout):
        await asyncio.sleep(timeout)  # 타임아웃 대기
        button.disabled = True  # 버튼 비활성화
        await message.edit(view=view)  # 메시지 업데이트

        # 타임아웃 메시지 전송
        await message.channel.send("시간이 초과되었습니다. 버튼이 비활성화되었습니다.")
        

    @app_commands.command(name="러시안룰렛", description="한명이 남을때까지 계속되는 살인게임") #파티참가를 클래스로 잘 수정해놔라.
    async def roulette(self, interaction: discord.Interaction):
        try:
            party = []
            async def wait(view, button, timeout):
                await asyncio.sleep(timeout)  # 타임아웃 대기
                button.disabled = True  # 버튼 비활성화
                embed = Embed(title=f"러시안 룰렛", description=f"로딩중...")
                await interaction.edit_original_response(embed=embed, view=view)

            async def join(interaction: discord.Interaction):
                player = interaction.user.name
                await interaction.response.defer()
                if not player in party: party.append(player) #파티에 참가한 유저를 리스트 업
                embed = Embed(title=f"러시안 룰렛", description=f"")
                embed.add_field(name="", value=f"{'\n'.join(party)}", inline=False)
                await interaction.edit_original_response(embed=embed, view=view)

            view = View()
            join_btn = Button(
                style=ButtonStyle.primary,
                label="참가",
                custom_id="join"
            )
            join_btn.callback = join
            view.add_item(join_btn)
            embed = Embed(title=f"러시안 룰렛", description=f"참가 대기중")
            menu = await interaction.response.send_message(embed=embed, view=view)
            voice = await voice_connect(self, interaction)
            
            await wait(view, join_btn, 5)#class로 리볼버 객체 만들어서 사운드 조절할것 발당 나누기 해서 대기시간 줄여서 탄 많을수록 재장전 속도 빠르게하기
            voice.play(FFmpegPCMAudio(source=f"{ASSET_SOUNDS}/{"open.mp3"}"))
            for turn in range(0, 7): #불발탄 추가로 형평성 만들기
                if voice.is_playing(): voice.stop()#나중에 사운드 플레이 라이브러리에 수정하기
                voice.play(FFmpegPCMAudio(source=f"{ASSET_SOUNDS}/{"bullet.mp3"}"))
                await asyncio.sleep(1)
            voice.play(FFmpegPCMAudio(source=f"{ASSET_SOUNDS}/{"open.mp3"}"))
            await asyncio.sleep(1)
            voice.play(FFmpegPCMAudio(source=f"{ASSET_SOUNDS}/{"triger.mp3"}"))

                # embed = Embed(title=f"러시안 룰렛", description=f"{party}")
                # await interaction.edit_original_response(embed=embed, view=view)



            

        except Exception as E:
            await interaction.channel.send(E)
            

# Cog 등록
async def setup(bot):
    await bot.add_cog(Game(bot))