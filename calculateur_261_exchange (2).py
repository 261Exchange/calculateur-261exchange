import streamlit as st
import requests
import datetime
import pandas as pd

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.image("https://261exchange.com/logo.png", width=200)
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

# Définition des services
services = {
    "Skrill": {"type": "usd", "frais": 0.0, "depot": 4750, "retrait": 4300},
    "Neteller": {"type": "usd", "frais": 0.0, "depot": 4750, "retrait": 4300},
    "Payeer": {"type": "usd", "frais": 0.0, "depot": 4750, "retrait": 4300},
    "AIRTM": {"type": "usd", "frais": 0.0, "depot": 4750, "retrait": 4300},
    "Tether BEP20": {"type": "crypto", "symbol": "binancecoin", "frais": 0.0, "depot": 4850, "retrait": 4300},
    "Tether TRC20": {"type": "crypto", "symbol": "tron", "frais": 0.0, "depot": 4850, "retrait": 4300},
    "Tron": {"type": "crypto", "symbol": "tron", "frais": 1.0, "depot": 4850, "retrait": 4300},
    "BNB": {"type": "crypto", "symbol": "binancecoin", "frais": 0.00009, "depot": 4850, "retrait": 4300},
    "BTC": {"type": "crypto", "symbol": "bitcoin", "frais": 0.00003, "depot": 4850, "retrait": 4300},
    "ETH": {"type": "crypto", "symbol": "ethereum", "frais": 0.0004, "depot": 4850, "retrait": 4300},
    "XRP": {"type": "crypto", "symbol": "ripple", "frais": 0.2, "depot": 4850, "retrait": 4300},
    "SOL": {"type": "crypto", "symbol": "solana", "frais": 0.001, "depot": 4850, "retrait": 4300},
    "Doge": {"type": "crypto", "symbol": "dogecoin", "frais": 1.0, "depot": 4850, "retrait": 4300},
    "LTC": {"type": "crypto", "symbol": "litecoin", "frais": 0.00015, "depot": 4850, "retrait": 4300},
    "SUI": {"type": "crypto", "symbol": "sui", "frais": 0.07, "depot": 4850, "retrait": 4300},
    "Toncoin": {"type": "crypto", "symbol": "the-open-network", "frais": 0.03, "depot": 4850, "retrait": 4300},
    "Matic": {"type": "crypto", "symbol": "matic-network", "frais": 1.0, "depot": 4850, "retrait": 4300},
    "Autres": {"type": "usd", "frais": 0.0, "depot": 4750, "retrait": 4400},
}

# Récupération des prix crypto
@st.cache_data(ttl=300)
def get_prices():
    ids = list({v["symbol"] for v in services.values() if v["type"] == "crypto"})
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd"
    r = requests.get(url)
    return r.json()

try:
    prices = get_prices()
except Exception as e:
    st.error(f"Erreur lors de la récupération des cours : {e}")
    st.stop()

# Choix utilisateur
operation = st.radio("Type d'opération :", ["💰 Dépôt ➜ Montant à envoyer", "📥 Montant reçu ➜ Ariary"])
service = st.selectbox("Service utilisé :", list(services.keys()))
info = services[service]
taux = info["depot"] if operation.startswith("💰") else info["retrait"]
st.caption(f"💡 Taux actuel : {taux:,} Ar/USD")

# Initialisation historique
if "historique" not in st.session_state:
    st.session_state.historique = []

# Variables d'affichage
montant_ariary = 0
montant_mga = 0
usd_net = "-"
crypto_net = "-"
frais = 0.0

# Dépôt vers USD ou Crypto
if operation == "💰 Dépôt ➜ Montant à envoyer":
    montant_mga = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)

    if st.button("✅ Valider le calcul"):
        usd = montant_mga / taux
        if info["type"] == "usd":
            frais = 0.58 if usd <= 35 and service in ["Skrill", "Neteller"] else usd * 0.0145 if service in ["Skrill", "Neteller"] else 0
            usd_net = usd - frais
            st.success(f"💵 Montant à envoyer : {usd_net:.2f} USD")
            st.write(f"🔸 Frais : {frais:.2f} USD")
        else:
            symbol = info["symbol"]
            if symbol not in prices:
                st.error(f"Cours indisponible pour {service}")
                st.stop()
            cours = prices[symbol]["usd"]
            crypto = usd / cours
            frais = info["frais"]
            crypto_net = crypto - frais
            st.success(f"🪙 Montant à envoyer : {crypto_net:.6f} {service}")
            st.write(f"🔸 Frais : {frais:.6f} {service}")

        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        st.session_state.historique.append({
            "Date": now,
            "Opération": operation,
            "Service": service,
            "Montant MGA": f"{montant_mga:.0f} Ar",
            "Montant USD/CRYPTO": f"{usd_net:.2f} USD" if info["type"] == "usd" else f"{crypto_net:.6f} {service}",
            "Frais": f"{frais:.2f} USD" if info["type"] == "usd" else f"{frais:.6f} {service}"
        })

# Réception vers Ariary
else:
    if info["type"] == "usd":
        montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, ste_
