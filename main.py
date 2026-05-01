import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import os

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1488515807892738151
SOOP_URL = "https://www.sooplive.com/station/kkcy2445"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

was_live = False

# :fire: 서버 유지용
app = Flask('')

@app.route('/')
def home():
    return "alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# :fire: 방송 상태 체크 (강화 버전)
def is_live():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(SOOP_URL, headers=headers, timeout=10)

        if res.status_code != 200:
            print("페이지 요청 실패:", res.status_code)
            return False

        soup = BeautifulSoup(res.text, "html.parser")

        # :one: 썸네일 확인
        og_image = soup.find("meta", property="og:image")
        img_url = og_image.get("content", "") if og_image else ""

        # :two: 텍스트 확인
        text = soup.get_text()

        print("이미지 URL:", img_url)
        print("LIVE 포함 여부:", "LIVE" in text or "방송" in text)

        # :fire: 조건 2개 이상 만족해야 True
        if "liveimg" in img_url and ("LIVE" in text or "방송" in text):
            return True

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

    # :fire: 방송 시작 감지
    if live and not was_live:
        embed = discord.Embed(
            title=":fire: 용님 방송 시작!",
            description="지금 바로 시청하러 가기",
            color=0x5865F2
        )
        embed.add_field(name=":link: 링크", value=SOOP_URL, inline=False)

        await channel.send(
            content="@everyone :fire: Yong Streaming ON!",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )

    was_live = live


keep_alive()
bot.run(TOKEN)
