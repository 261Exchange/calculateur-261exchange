import streamlit as st
import requests
import datetime
import pandas as pd

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.image("https://261exchange.com/logo.png", width=200)
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant à envoyer ou à recevoir selon le service utilisé.")

# === CONFIGURATION SERVICES ===
services = {
    "Neteller": {"type": "fiat", "depot": 4750, "retrait": 4300, "frais_depot": "auto"},
    "Skrill": {"type": "fiat", "depot": 4750, "retrait": 4300, "frais_depot": "auto"},
    "Payeer": {"type": "fiat", "depot": 4750, "retrait": 4300, "frais_depot": 0},
    "AIRTM": {"type": "fiat", "depot": 4750, "retrait": 4300, "frais_depot": 0},
    "Tether BEP20": {"type": "fiat", "depot": 4750, "retrait": 4300, "frais_depot": 0},
    "Tether TRC20": {"type": "crypto", "depot": 4850, "retrait": 4300, "frais_depot": 1},

    # Crypto avec frais en token natif
    "Tron": {"id": "tron", "symbol": "TRX", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 1},
    "BNB": {"id": "binancecoin", "symbol": "BNB", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 0.00009},
    "ETH": {"id": "ethereum", "symbol": "ETH", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 0.0004},
    "BTC": {"id": "bitcoin", "symbol": "BTC", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 0.00003},
    "XRP": {"id": "ripple", "symbol": "XRP", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 0.2},
    "SOL": {"id": "solana", "symbol": "SOL", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 0.001},
    "Doge": {"id": "dogecoin", "symbol": "DOGE", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 1},
    "LTC": {"id": "litecoin", "symbol": "LTC", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 0.00015},
    "SUI": {"id": "sui", "symbol": "SUI", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 0.07},
    "Toncoin": {"id": "the-open-network", "symbol": "TON", "type": "crypto", "depot": 4850, "retrait": 4300, "frais_token": 0.03},
}

# === RÉCUPÉRATION COURS CRYPTOS ===
@st.cache_data(ttl=300)
def get_prices():
    ids = [v["id"] for v in services.values() if v.get("id")]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd"
    res = requests.get(url)
    return res.json()

try:
    prices = get_prices()
except Exception as e:
    st.error(f"Erreur de récupération des cours : {e}")
    st.stop()

# === INTERFACE UTILISATEUR ===
operation = st.radio("Type d'opération :", ["🔁 Dépôt (Ariary ➜ USD ou Crypto)", "🔁 Retrait (USD ou Crypto ➜ Ariary)"])
service_name = st.selectbox("Choisissez le service :", list(services.keys()))
service = services[service_name]
taux = service["depot"] if "Dépôt" in operation else service["retrait"]

# === CALCUL ===
if "Dépôt" in operation:
    montant_mga = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
    montant_usd = montant_mga / taux

    if service["type"] == "crypto":
        cours_usd = prices[service["id"]]["usd"]
        montant_crypto = montant_usd / cours_usd
        net = montant_crypto - service.get("frais_token", 0)
        st.markdown("### 📊 Résultat")
        st.write(f"✅ {net:.6f} {service['symbol']} à envoyer")
        st.write(f"💸 Frais : {service.get('frais_token', 0)} {service['symbol']}")
    else:
        frais = 0
        if service.get("frais_depot") == "auto":
            frais = 0.58 if montant_usd <= 35 else montant_usd * 0.0145
        else:
            frais = service.get("frais_depot", 0)
        net = montant_usd - frais
        st.markdown("### 📊 Résultat")
        st.write(f"✅ {net:.2f} USD à envoyer")
        st.write(f"💸 Frais : {frais:.2f} USD")

else:
    montant_usd = st.number_input("Montant à envoyer (en USD ou Crypto)", min_value=0.0, step=1.0)
    montant_mga = montant_usd * taux

    if service["type"] == "crypto":
        cours_usd = prices[service["id"]]["usd"]
        montant_crypto = montant_usd / cours_usd
        total = montant_crypto + service.get("frais_token", 0)
        st.markdown("### 📊 Résultat")
        st.write(f"🪙 {total:.6f} {service['symbol']} à recevoir")
        st.write(f"💰 Total en Ariary : {montant_mga:.0f} Ar")
        st.write(f"🧾 Frais : {service.get('frais_token', 0)} {service['symbol']}")
    else:
        st.markdown("### 📊 Résultat")
        st.write(f"🪙 {montant_usd:.2f} USD à recevoir")
        st.write(f"💰 Montant total en Ariary : {montant_mga:.0f} Ar")

# === HISTORIQUE ===
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Type": operation,
    "Service": service_name,
    "Ariary": f"{montant_mga:.0f} Ar",
    "Montant USD/Crypto": f"{net:.6f}" if "Dépôt" in operation else f"{montant_usd:.6f}",
})

df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter CSV", df.to_csv(index=False).encode(), file_name="historique_261.csv", mime="text/csv")
if st.checkbox("📜 Voir l'historique"):
    st.dataframe(df)
