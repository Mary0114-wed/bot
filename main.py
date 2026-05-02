import discord
from discord.ext import commands, tasks
import requests
import os
import json
import time
from datetime import datetime, timedelta

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1488515807892738151
BJ_ID = "kkcy2445"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 🔥 상태 저장
# =========================
STATE_FILE = "stream_state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "live": False,
            "last_start": "",
            "last_event_time": 0
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
candidate = None
confirm_count = 0

off_since = None
OFF_CONFIRM_SEC = 180  # 3분 OFF 유지

# =========================
# 🔥 API
# =========================
def fetch_broad_start():
    url = "https://st.sooplive.com/api/get_station_status.php"
    params = {"szBjId": BJ_ID}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        data = res.json()
        return data.get("DATA", {}).get("broad_start", "")
    except:
        return ""


# =========================
# 🔥 핵심 LIVE 판정 (오탐 방지 핵심)
# =========================
def is_real_live(broad_start):
    if not broad_start:
        return False

    try:
        start = datetime.strptime(broad_start, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()

        diff = now - start

        # 🔥 너무 오래된 start = 잔상 제거
        if diff > timedelta(hours=12):
            return False

        # 🔥 최근 시작만 LIVE 인정
        if diff < timedelta(seconds=30):
            return True

        # 🔥 기본 유지 조건
        return True

    except:
        return False


# =========================
# 🔥 시작
# =========================
@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료!")
    stream_loop.start()


# =========================
# 🔥 메인 루프
# =========================
@tasks.loop(seconds=15)
async def stream_loop():
    global candidate, confirm_count, off_since, state

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    broad_start = fetch_broad_start()
    live = is_real_live(broad_start)

    now = time.time()

    # =========================
    # 🔥 OFF 안정화 (3분 유지)
    # =========================
    if not live:
        if off_since is None:
            off_since = now
            return

        if now - off_since < OFF_CONFIRM_SEC:
            return

    else:
        off_since = None


    # =========================
    # 🔥 3회 연속 확인 (API 흔들림 제거)
    # =========================
    if candidate != live:
        candidate = live
        confirm_count = 1
        return

    confirm_count += 1
    if confirm_count < 3:
        return


    # =========================
    # 🔥 상태 변화 없으면 종료
    # =========================
    if state["live"] == live:
        return


    # =========================
    # 🔥 상태 확정
    # =========================
    state["live"] = live
    save_state(state)


    # =========================
    # 🔥 LIVE ON
    # =========================
    if live:
        # 같은 방송이면 중복 차단
        if state["last_start"] == broad_start:
            return

        state["last_start"] = broad_start
        state["last_event_time"] = now
        save_state(state)

        print("🚨 방송 시작 확정")

        embed = discord.Embed(
            title="🔥 방송 시작!",
            description="방송 시청 하러가기",
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
    # 🔥 OFF
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
