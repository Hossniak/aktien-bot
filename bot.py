import os
import requests
import pandas as pd
import yfinance as yf

# ==========================================
# 1. KONFIGURATION
# ==========================================
TELEGRAM_TOKEN = "8698312950:AAEgdICs_IYu_P_xRmldQq6Bdj-7A0twhRM"
TELEGRAM_CHAT_ID = "8800187045"

AKTIEN_LISTE = {
    "SAP.DE": "SAP",
    "SIE.DE": "Siemens",
    "ALV.DE": "Allianz",
    "DTE.DE": "Deutsche Telekom",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "KO": "Coca-Cola",
}

# ==========================================
# 2. HELFER-FUNKTIONEN
# ==========================================
def send_telegram_message(message):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Fehler beim Telegram-Versand: {e}")

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ==========================================
# 3. ANALYSE-LOGIK
# ==========================================
def check_signals():
    print("Starte Aktien-Check...")

    for ticker, name in AKTIEN_LISTE.items():
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)

            if df.empty or len(df) < 200:
                print(f"Nicht genug Daten fuer {name}")
                continue

            df["SMA200"] = df["Close"].rolling(window=200).mean()
            df["RSI"] = calculate_rsi(df["Close"], window=14)

            current_price = float(df["Close"].iloc[-1])
            current_sma = float(df["SMA200"].iloc[-1])
            current_rsi = float(df["RSI"].iloc[-1])

            print(f"{name}: Kurs={current_price:.2f}, RSI={current_rsi:.1f}")

            if current_price > current_sma and current_rsi <= 35:
                msg = (
                    f"🟢 *KAUFEMPFEHLUNG: {name} ({ticker})*\n"
                    f"Der Kurs ist im Aufwärtstrend, aber kurzfristig überverkauft.\n"
                    f"• Kurs: {current_price:.2f}\n"
                    f"• RSI (14d): {current_rsi:.1f}"
                )
                send_telegram_message(msg)
                print(f"-> Signal gesendet (Kauf)")

            elif current_rsi >= 70:
                msg = (
                    f"🔴 *VERKAUFSEMPFEHLUNG: {name} ({ticker})*\n"
                    f"Die Aktie ist kurzfristig überhitzt (überkauft).\n"
                    f"• Kurs: {current_price:.2f}\n"
                    f"• RSI (14d): {current_rsi:.1f}"
                )
                send_telegram_message(msg)
                print(f"-> Signal gesendet (Verkauf)")

        except Exception as e:
            print(f"Fehler bei {ticker}: {e}")

    print("Check beendet.")

if __name__ == "__main__":
    check_signals()
