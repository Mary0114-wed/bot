import discord
from discord.ext import commands, tasks
import requests
import os
import time
import asyncio

TOKEN = os.environ.get("TOKEN")  # 또는 직접 넣어도 됨
CHANNEL_ID = 1488515807892738151
BJ_ID = "kkcy2445"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

was_live = False


def is_live():
    url = "https://st.sooplive.com/api/get_station_status.php"
    params = {"szBjId": BJ_ID}
    headers = {"User-Agent": "Mozilla/5.0"}

    for i in range(3):
        try:
            res = requests.get(url, params=params, headers=headers, timeout=10)

            print(f"[API 응답 코드]: {res.status_code}")

            if res.status_code != 200:
                time.sleep(1)
                continue

            data = res.json()
            status = data.get("broad_status")

            print("현재 상태:", status)

            return status == "ON"

        except Exception as e:
            print(f"[에러 {i+1}]:", e)
            time.sleep(1)

    return False


@bot.event
async def on_ready():
    global was_live
    print(":fire: on_ready 실행됨")
    print(f"{bot.user} 로그인 완료!")

    was_live = is_live()
    print("초기 상태:", was_live)

    check_stream.start()
    print(":fire: 루프 시작됨")

    # :fire: 컨테이너 종료 방지용 루프
    while True:
        await asyncio.sleep(60)


@tasks.loop(seconds=20)
async def check_stream():
    global was_live

    print(":arrows_counterclockwise: 체크 실행됨")

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print(":x: 채널 못 찾음")
        return

    live = is_live()

    if live and not was_live:
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

    was_live = live


bot.run(TOKEN)
