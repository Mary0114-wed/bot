import discord
from discord.ext import commands, tasks
import requests
import os
import time

TOKEN = os.environ.get("TOKEN")  # 또는 "봇토큰"
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

            if res.status_code != 200:
                time.sleep(1)
                continue

            data = res.json()
            return data.get("broad_status") == "ON"

        except:
            time.sleep(1)

    return False


@bot.event
async def on_ready():
    global was_live
    print(f"{bot.user} 로그인 완료!")

    was_live = is_live()
    check_stream.start()


@tasks.loop(seconds=20)
async def check_stream():
    global was_live

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return

    live = is_live()

    if live and not was_live:
        embed = discord.Embed(
            title=":fire: Yong님 방송 시작!",
            description="지금 바로 시청하러 가기",
            color=0x5865F2
        )

        # :fire: 링크 그냥 고정
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

        print("알림 보냄!")

    was_live = live


bot.run(TOKEN)
