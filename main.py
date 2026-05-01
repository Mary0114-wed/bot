import discord
from discord.ext import commands, tasks
import requests
import os
import asyncio

TOKEN = os.environ.get("TOKEN")  # 또는 "봇토큰"
CHANNEL_ID = 1488515807892738151
BJ_ID = "kkcy2445"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

last_broad_start = ""  # :fire: 핵심


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


@bot.event
async def on_ready():
    global last_broad_start

    print(f"{bot.user} 로그인 완료!")

    # :fire: 현재 상태 저장 (중복 알림 방지)
    last_broad_start = get_broadcast_start()

    check_stream.start()

    # :fire: 컨테이너 유지
    while True:
        await asyncio.sleep(60)


@tasks.loop(seconds=20)
async def check_stream():
    global last_broad_start

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("채널 못 찾음")
        return

    current_start = get_broadcast_start()

    # :fire: 방송 새로 시작 감지
    if current_start and current_start != last_broad_start:
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

        print(":white_check_mark: 알림 보냄!")

    # :fire: 상태 업데이트
    last_broad_start = current_start


bot.run(TOKEN)
