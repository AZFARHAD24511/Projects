# %%
# pip install python-binance pandas
from binance.client import Client
import pandas as pd
import time, os
from datetime import datetime, timedelta

# -----------------------
# تنظیمات (ویرایش‌پذیر)
# -----------------------
API_KEY = ""         # اختیاری، اگر دارید قرار بدید
API_SECRET = ""      # اختیاری
SYMBOL = "PAXGUSDT"  # ← اگر می‌خوای عوض کنی: "PAXGUSDC" یا "PAXGBUSD"
INTERVAL = Client.KLINE_INTERVAL_30MINUTE
START_STR = "1 Jan 2025"
END_STR = None


# chunk size (تعداد روز در هر درخواست). 30 روز معمولاً مناسب است.
CHUNK_DAYS = 30

# نرخ‌محدودیت و retry
SLEEP_BETWEEN_CHUNKS = 0.3
MAX_RETRIES = 5
RETRY_BACKOFF = 2.0  # ضرب‌کننده نمایی برای backoff

# -----------------------
# آماده‌سازی/اتصال
# -----------------------
client = Client(API_KEY, API_SECRET)

def iter_chunks(start_str, end_str, days=CHUNK_DAYS):
    fmt = "%d %b %Y"
    start = datetime.strptime(start_str, fmt)

    # ← اگر end_str برابر None بود، برو تا همین لحظه
    if end_str is None:
        end = datetime.utcnow()
    else:
        end = datetime.strptime(end_str, fmt)

    cur = start
    while cur < end:
        nxt = min(cur + timedelta(days=days), end)
        # include time so Binance covers full chunk
        yield cur.strftime("%d %b %Y %H:%M:%S"), (nxt + timedelta(hours=23, minutes=59, seconds=59)).strftime("%d %b %Y %H:%M:%S")
        cur = nxt + timedelta(seconds=1)


all_rows = []
total_chunks = 0
for s, e in iter_chunks(START_STR, END_STR, CHUNK_DAYS):
    total_chunks += 1
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            klines = client.get_historical_klines(SYMBOL, INTERVAL, s, e)
            break
        except Exception as exc:
            attempt += 1
            wait = (RETRY_BACKOFF ** attempt) * 0.5
            print(f"Chunk error ({s} -> {e}), attempt {attempt}/{MAX_RETRIES}: {exc}. waiting {wait:.1f}s")
            time.sleep(wait)
    else:
        # پس از چند تلاش ناموفق، از این chunk می‌گذریم
        print(f"Skipping chunk after {MAX_RETRIES} failed attempts: {s} -> {e}")
        continue

    if not klines:
        # ممکن است هیچ داده‌ای برای این بازه وجود نداشته باشد
        time.sleep(SLEEP_BETWEEN_CHUNKS)
        continue

    # هر k: [open_time, open, high, low, close, volume, close_time, ...]
    for k in klines:
        # محافظت در برابر فرمت ناقص
        try:
            open_time = int(k[0])
            open_p = float(k[1])
            high_p = float(k[2])
            low_p = float(k[3])
            close_p = float(k[4])
            vol = float(k[5])
        except Exception:
            continue
        all_rows.append([open_time, open_p, high_p, low_p, close_p, vol])

    time.sleep(SLEEP_BETWEEN_CHUNKS)

# -----------------------
# ساخت DataFrame نهایی
# -----------------------
if not all_rows:
    raise RuntimeError("No rows fetched. Check SYMBOL, interval, or API limits.")

df = pd.DataFrame(all_rows, columns=['open_time_ms','open','high','low','close','volume'])
# تبدیل به timestamp
df['timestamp'] = pd.to_datetime(df['open_time_ms'].astype(int), unit='ms', utc=True)
# مرتب، حذف تکراری، و تبدیل به timezone محلی (اختیاری)
df = df.sort_values('timestamp').drop_duplicates(subset='timestamp', keep='first').reset_index(drop=True)
# اگر می‌خوای timestamp به محلی (بدون tz) تبدیل بشه:
df['timestamp'] = pd.to_datetime(df['open_time_ms'], unit='ms', utc=True)
df['timestamp'] = df['timestamp'].dt.tz_localize(None)


# انتخاب ستون‌های خروجی و تبدیل دقیق
df_out = df[['timestamp','open','high','low','close','volume']].copy()
df_out[['open','high','low','close','volume']] = df_out[['open','high','low','close','volume']].astype(float)

print("Range:", df_out['timestamp'].min(), "->", df_out['timestamp'].max())




