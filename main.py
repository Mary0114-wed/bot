import discord
from discord.ext import commands, tasks
import requests
import os
import asyncio
import json
import time

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1491439774173499553
BJ_ID = "kkcy2445"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 🔥 상태 저장 파일
# =========================
STATE_FILE = "stream_state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "live": False,
            "notified_start": "",
        }
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


state = load_state()

# =========================
# 🔥 안정화 변수
# =========================
candidate_live = None
confirm_count = 0

off_since = None
OFF_CONFIRM_SECONDS = 120  # 🔥 2분 유지 후 OFF 확정


# =========================
# 🔥 API
# =========================
def get_broadcast_start():
    url = "https://st.sooplive.com/api/get_station_status.php"
    params = {"szBjId": BJ_ID}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        data = res.json()

        info = data.get("DATA", {})
        return info.get("broad_start", "")

    except Exception as e:
        print("API 에러:", e)
        return ""


def is_live(broad_start):
    return bool(broad_start)


# =========================
# 🔥 시작
# =========================
@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료!")
    stream_check.start()


# =========================
# 🔥 메인 루프
# =========================
@tasks.loop(seconds=15)
async def stream_check():
    global candidate_live, confirm_count, off_since, state

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    broad_start = get_broadcast_start()
    live = is_live(broad_start)

    now = time.time()

    # =========================
    # 🔥 1. OFF 쿨다운 처리 (핵심)
    # =========================
    if not live:
        if off_since is None:
            off_since = now
            return

        # 2분 미만이면 아직 OFF 아님
        if now - off_since < OFF_CONFIRM_SECONDS:
            return

    else:
        off_since = None


    # =========================
    # 🔥 2. 3회 연속 확인 (API 흔들림 제거)
    # =========================
    if candidate_live != live:
        candidate_live = live
        confirm_count = 1
        return

    confirm_count += 1
    if confirm_count < 3:
        return


    # =========================
    # 🔥 3. 상태 변화 없으면 종료
    # =========================
    if state["live"] == live:
        return


    # =========================
    # 🔥 4. 상태 확정
    # =========================
    state["live"] = live
    save_state(state)


    # =========================
    # 🔥 LIVE ON (완전 중복 방지)
    # =========================
    if live:
        if state["notified_start"] == broad_start:
            return

        state["notified_start"] = broad_start
        save_state(state)

        print("🚨 방송 시작 확정")

        embed = discord.Embed(
            title="🔥 방송 시작!",
            description="지금 시청 가능합니다",
            color=0x5865F2
        )

        embed.add_field(
            name="🔗 링크",
            value="https://www.sooplive.com/station/kkcy2445",
            inline=False
        )

        await channel.send(
            "@everyone 🔥 LIVE ON!",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )


    # =========================
    # 🔥 OFF (지연 방지 완료)
    # =========================
    else:
        print("🛑 방송 종료 확정")

        embed = discord.Embed(
            title="🛑 방송 종료",
            description="방송이 종료되었습니다",
            color=0xFF3B30
        )

        await channel.send(embed=embed)


bot.run(TOKEN)
