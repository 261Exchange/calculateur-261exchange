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

# === Calculs ===
if operation == "💰 Dépôt ➜ Montant à envoyer":
    if info["type"] == "usd":
        montant_mga = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
        usd = montant_mga / taux
        # Frais spécifique pour Skrill & Neteller
        if service in ["Skrill", "Neteller"]:
            frais = 0.58 if usd <= 35 else usd * 0.0145
            usd_net = usd - frais
        else:
            frais = 0
            usd_net = usd
        st.success(f"💵 Montant à envoyer : {usd_net:.2f} USD")
        st.write(f"🔸 Frais : {frais:.2f} USD")
    else:
        montant_mga = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
        usd = montant_mga / taux
        cours = prices[info["symbol"]]["usd"]
        crypto = usd / cours
        frais = info["frais"]
        crypto_net = crypto - frais
        st.success(f"🪙 Montant à envoyer : {crypto_net:.6f} {service}")
        st.write(f"🔸 Frais : {frais:.6f} {service}")

else:
    if info["type"] == "usd":
        montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=1.0)
        montant_ariary = montant_usd * taux
        frais = 0
        st.success(f"💵 Montant à recevoir : {montant_ariary:.0f} Ar (Frais inclus)")
    else:
        montant_crypto = st.number_input(f"Montant reçu (en {service})", min_value=0.0, step=0.0001)
        frais = info["frais"]
        cours = prices[info["symbol"]]["usd"]
        montant_usd = (montant_crypto - frais) * cours
        montant_ariary = montant_usd * taux
        st.success(f"💵 Montant à recevoir : {montant_ariary:.0f} Ar (Frais inclus)")
        st.write(f"🔸 Frais déduits : {frais:.6f} {service}")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Opération": operation,
    "Service": service,
    "Montant MGA": f"{montant_ariary:.0f} Ar" if 'montant_ariary' in locals() else f"{montant_mga:.0f} Ar",
    "Montant USD/CRYPTO": f"{usd_net:.2f} USD" if 'usd_net' in locals() else f"{crypto_net:.6f} {service}" if 'crypto_net' in locals() else "-",
    "Frais": f"{frais:.2f} USD" if info["type"] == "usd" else f"{frais:.6f} {service}"
})

# Export CSV
df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter historique CSV", df.to_csv(index=False).encode(), file_name="historique_261_exchange.csv", mime="text/csv")

if st.checkbox("📜 Voir l'historique"):
    st.dataframe(df)
