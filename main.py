import discord
from discord.ext import commands, tasks
import requests
import os
import asyncio
from datetime import datetime, timedelta

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1491439774173499553
BJ_ID = "kkcy2445"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

last_broad_start = ""
was_live = False


def get_broadcast_start():
    url = "https://st.sooplive.com/api/get_station_status.php"
    params = {"szBjId": BJ_ID}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        data = res.json()

        info = data.get("DATA", {})
        broad_start = info.get("broad_start", "")

        print("broad_start:", broad_start)

        return broad_start

    except Exception as e:
        print("에러:", e)
        return ""


def is_live(broad_start):
    if not broad_start:
        return False

    try:
        start_time = datetime.strptime(broad_start, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()

        diff = now - start_time
        print("방송 경과 시간:", diff)

        # :fire: 24시간 기준 (길게 잡아서 오탐 최소화)
        if diff > timedelta(hours=24):
            return False

        return True

    except Exception as e:
        print("시간 파싱 에러:", e)
        return False


@bot.event
async def on_ready():
    global last_broad_start, was_live

    print(f"{bot.user} 로그인 완료!")

    last_broad_start = get_broadcast_start()
    was_live = is_live(last_broad_start)

    print("초기 상태:", was_live)

    check_stream.start()

    while True:
        await asyncio.sleep(60)


@tasks.loop(seconds=20)
async def check_stream():
    global last_broad_start, was_live

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("채널 못 찾음")
        return

    current_start = get_broadcast_start()
    live = is_live(current_start)

    # :fire: 방송 시작 감지
    if live and (not was_live or current_start != last_broad_start):
        print(":rotating_light: 방송 시작 감지!")

        embed = discord.Embed(
            title=":fire: Yong님 방송 시작!",
            description="지금 바로 시청하러 가기",
            color=0x5865F2
        )

        embed.add_field(
            name=":link: 링크",
            value="<https://www.sooplive.com/station/kkcy2445>",
            inline=False
        )

        await channel.send(
            content="@everyone :fire: Yong Streaming ON!",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )

        print(":white_check_mark: 시작 알림 보냄!")

    # :fire: 방송 종료 감지
    if not live and was_live:
        print(":octagonal_sign: 방송 종료 감지!")

        embed = discord.Embed(
            title=":octagonal_sign: Yong님 방송 종료",
            description="방송이 종료되었습니다",
            color=0xFF3B30
        )

        await channel.send(embed=embed)

        print(":white_check_mark: 종료 알림 보냄!")

    # 상태 업데이트
    was_live = live
    last_broad_start = current_start


bot.run(TOKEN)
