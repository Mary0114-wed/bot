import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1488515807892738151
SOOP_URL = "https://www.sooplive.com/station/kkcy2445"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

was_live = False

def is_live():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(SOOP_URL, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # :fire: 메타 태그 기반 체크 (썸네일 낚시 방지)
        meta_title = soup.find("meta", property="og:title")

        if meta_title:
            content = meta_title.get("content", "")
            print("현재 제목:", content)
            return "LIVE" in content or "방송중" in content

        return False
    except Exception as e:
        print("에러:", e)
        return False


@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료!")
    check_stream.start()


@tasks.loop(seconds=60)
async def check_stream():
    global was_live

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print("채널 못 찾음")
        return

    live = is_live()
    print("현재 방송 상태:", live)

    if live and not was_live:
        embed = discord.Embed(
            title=":fire: 방송 시작!",
            description="지금 바로 시청하러 가기",
            color=0x5865F2
        )
        embed.add_field(name=":link: 링크", value=SOOP_URL, inline=False)

        await channel.send(
            content="@everyone :fire: 방송 시작!",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )

    was_live = live


bot.run(TOKEN)
