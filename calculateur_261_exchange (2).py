import streamlit as st
import requests
import datetime
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

# === Définition des services ===
crypto_services = {
    "tron": {"symbol": "TRX", "fee": 1},
    "bitcoin": {"symbol": "BTC", "fee": 0.00003},
    "ethereum": {"symbol": "ETH", "fee": 0.0004},
    "binancecoin": {"symbol": "BNB", "fee": 0.00009},
    "ripple": {"symbol": "XRP", "fee": 0.2},
    "dogecoin": {"symbol": "DOGE", "fee": 1},
    "solana": {"symbol": "SOL", "fee": 0.001},
    "litecoin": {"symbol": "LTC", "fee": 0.00015},
    "sui": {"symbol": "SUI", "fee": 0.07},
    "toncoin": {"symbol": "TON", "fee": 0.03}
}

fiat_services = {
    "Skrill": {"depot": 4750, "retrait": 4300, "fee": lambda usd: 0.58 if usd <= 35 else usd * 0.0145},
    "Neteller": {"depot": 4750, "retrait": 4300, "fee": lambda usd: 0.58 if usd <= 35 else usd * 0.0145},
    "Payeer": {"depot": 4750, "retrait": 4300, "fee": lambda usd: 0.0},
    "AIRTM": {"depot": 4750, "retrait": 4300, "fee": lambda usd: 0.0},
    "Tether BEP20": {"depot": 4750, "retrait": 4300, "fee": lambda usd: 0.0}
}

autres_services = {
    "Autres": {"depot": 4750, "retrait": 4400, "fee": lambda usd: 0.0}
}

# Combine tous les services
tous_services = {**{k: v for k, v in crypto_services.items()}, **fiat_services, **autres_services}

# Récupération des cours crypto
@st.cache_data(ttl=300)
def get_prices():
    ids = ",".join(crypto_services.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    res = requests.get(url)
    return res.json()

try:
    prices = get_prices()
except Exception as e:
    st.error(f"Erreur de récupération des cours : {e}")
    st.stop()

operation = st.radio("Type d'opération :", ["🔁 Dépôt ➜ USD/Crypto", "🔁 Retrait USD ➜ Crypto"])
service = st.selectbox("Choisissez le service :", list(tous_services.keys()))

# Prix unitaire si crypto
if service in crypto_services:
    st.info(f"💲 Prix unitaire : {prices[service]['usd']} USD par {crypto_services[service]['symbol']}")

# Champs d'entrée
if operation == "🔁 Dépôt ➜ USD/Crypto":
    montant_mga = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
else:
    montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=1.0)

# Déterminer le taux et frais
if service in crypto_services:
    taux = 4850 if operation.startswith("🔁 Dépôt") else 4300
    fee = crypto_services[service]['fee']
    symbol = crypto_services[service]['symbol']
    prix_usd = prices[service]['usd']
    if operation.startswith("🔁 Dépôt"):
        usd = montant_mga / taux
        crypto_amount = usd / prix_usd
        final = crypto_amount - fee
        result_text = f"{final:.6f} {symbol} à envoyer | {montant_mga:.0f} Ar"
        st.write(f"✅ Montant à envoyer : **{final:.6f} {symbol}**")
        st.write(f"💸 Frais : {fee} {symbol}")
    else:
        crypto_amount = montant_usd / prix_usd
        final = crypto_amount + fee
        ar = montant_usd * taux
        result_text = f"{final:.6f} {symbol} à recevoir | {ar:.0f} Ar"
        st.write(f"🪙 Montant à recevoir : **{final:.6f} {symbol}**")
        st.write(f"💰 Montant total en Ariary : **{ar:.0f} Ar**")
        st.write(f"🧾 Frais inclus : {fee} {symbol}")
else:
    taux = fiat_services.get(service, autres_services['Autres'])["depot"] if operation.startswith("🔁 Dépôt") else fiat_services.get(service, autres_services['Autres'])["retrait"]
    if operation.startswith("🔁 Dépôt"):
        usd = montant_mga / taux
        fee = tous_services[service]['fee'](usd)
        total = usd - fee
        result_text = f"{total:.2f} USD | {montant_mga:.0f} Ar"
        st.write(f"✅ Montant à envoyer : **{total:.2f} USD**")
        st.write(f"💸 Frais : {fee:.2f} USD")
    else:
        ar = montant_usd * taux
        result_text = f"{montant_usd:.2f} USD | {ar:.0f} Ar"
        st.write(f"🪙 Montant reçu : **{montant_usd:.2f} USD**")
        st.write(f"💰 Montant en Ariary : **{ar:.0f} Ar**")

# Copier résultat
if st.button("📋 Copier le résultat"):
    st.code(result_text)

# Export PNG

def generate_png(text):
    img = Image.new("RGB", (700, 150), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    draw.text((20, 60), text, fill=(0, 0, 0), font=font)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

if "result_text" in locals():
    st.download_button(
        label="⬇️ Télécharger en PNG",
        data=generate_png(result_text),
        file_name="resultat_261exchange.png",
        mime="image/png"
    )

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []
now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Service": service,
    "Opération": operation,
    "Résultat": result_text
})

st.download_button("⬇️ Export CSV", pd.DataFrame(st.session_state.historique).to_csv(index=False).encode(), file_name="historique.csv")

if st.checkbox("📜 Voir l'historique"):
    st.dataframe(pd.DataFrame(st.session_state.historique))
