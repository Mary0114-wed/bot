import discord
from discord.ext import commands, tasks
import requests
import os
import json
import time

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1491439774173499553
BJ_ID = "kkcy2445"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

STATE_FILE = "stream_state.json"

# =========================
# 🔥 상태 로딩
# =========================
def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "live": False,
            "last_broad_start": "",
            "last_event": 0
        }
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

state = load_state()

# =========================
# 🔥 API
# =========================
def fetch_broad_start():
    url = "https://st.sooplive.com/api/get_station_status.php"
    params = {"szBjId": BJ_ID}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        return data.get("DATA", {}).get("broad_start", "")
    except:
        return ""


# =========================
# 🔥 핵심 판단 로직 (진짜 중요)
# =========================
def detect_state(broad_start, last_start, prev_live):
    """
    TRUE = LIVE
    FALSE = OFF
    """

    # OFF 조건
    if not broad_start:
        return False

    # 방송 새로 시작된 경우만 LIVE
    if broad_start != last_start:
        return True

    # 기존 상태 유지
    return prev_live


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
    global state

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    broad_start = fetch_broad_start()

    prev_live = state["live"]
    last_start = state["last_broad_start"]

    # =========================
    # 🔥 상태 판단
    # =========================
    live = detect_state(broad_start, last_start, prev_live)

    # =========================
    # 🔥 변화 없으면 종료
    # =========================
    if live == prev_live:
        return


    # =========================
    # 🔥 상태 업데이트
    # =========================
    state["live"] = live
    state["last_broad_start"] = broad_start
    state["last_event"] = time.time()
    save_state(state)


    # =========================
    # 🔥 LIVE ON
    # =========================
    if live:
        print("🚨 방송 시작 이벤트")

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

        await channel.send("@everyone 🔥 LIVE ON!", embed=embed)


    # =========================
    # 🔥 OFF
    # =========================
    else:
        print("🛑 방송 종료 이벤트")

        embed = discord.Embed(
            title="🛑 방송 종료",
            description="방송이 종료되었습니다",
            color=0xFF3B30
        )

        await channel.send(embed=embed)


bot.run(TOKEN)
