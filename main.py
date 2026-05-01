import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import os

# :closed_lock_with_key: 환경변수에서 토큰 가져오기
TOKEN = os.environ.get("TOKEN")

# :pushpin: 설정
CHANNEL_ID = 1488515807892738151
SOOP_URL = "https://www.sooplive.com/station/kkcy2445"

# :wrench: 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

was_live = False

# :mag: 방송 상태 확인 함수
def is_live():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(SOOP_URL, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        return "방송중" in soup.get_text()
    except Exception as e:
        print("에러:", e)
        return False

# :robot: 봇 준비 완료
@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료!")
    check_stream.start()

# :repeat: 60초마다 체크
@tasks.loop(seconds=60)
async def check_stream():
    global was_live

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print("채널 못 찾음")
        return

    live = is_live()

    if live and not was_live:
        embed = discord.Embed(
            title=":fire: 용님 방송 시작!",
            description="지금 바로 시청하러 가기",
            color=0x5865F2
        )
        embed.add_field(name=":link: 링크", value=SOOP_URL, inline=False)

        await channel.send(
            content="@everyone :fire: 용 Streaming on!",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )

    was_live = live

# :rocket: 실행
bot.run(TOKEN)