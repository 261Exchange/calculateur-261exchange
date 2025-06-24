import streamlit as st
import requests
import datetime
import pandas as pd

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

# Définir les services disponibles
services_info = {
    "Skrill": {"type": "usd", "depot": 4750, "retrait": 4300, "frais": lambda usd: 0.58 if usd <= 35 else usd * 0.0145},
    "Neteller": {"type": "usd", "depot": 4750, "retrait": 4300, "frais": lambda usd: 0.58 if usd <= 35 else usd * 0.0145},
    "Payeer": {"type": "usd", "depot": 4750, "retrait": 4300, "frais": lambda usd: 0},
    "AIRTM": {"type": "usd", "depot": 4750, "retrait": 4300, "frais": lambda usd: 0},
    "Tether BEP20": {"type": "crypto", "symbol": "tether", "depot": 4750, "retrait": 4300, "frais": 0},
    "Tron": {"type": "crypto", "symbol": "tron", "depot": 4850, "retrait": 4300, "frais": 1},
    "BNB": {"type": "crypto", "symbol": "binancecoin", "depot": 4850, "retrait": 4300, "frais": 0.00009},
    "Ethereum": {"type": "crypto", "symbol": "ethereum", "depot": 4850, "retrait": 4300, "frais": 0.0004},
    "Bitcoin": {"type": "crypto", "symbol": "bitcoin", "depot": 4850, "retrait": 4300, "frais": 0.00003},
    "XRP": {"type": "crypto", "symbol": "ripple", "depot": 4850, "retrait": 4300, "frais": 0.2},
    "Solana": {"type": "crypto", "symbol": "solana", "depot": 4850, "retrait": 4300, "frais": 0.001},
    "Doge": {"type": "crypto", "symbol": "dogecoin", "depot": 4850, "retrait": 4300, "frais": 1},
    "Litecoin": {"type": "crypto", "symbol": "litecoin", "depot": 4850, "retrait": 4300, "frais": 0.00015},
    "SUI": {"type": "crypto", "symbol": "sui", "depot": 4850, "retrait": 4300, "frais": 0.07},
    "Toncoin": {"type": "crypto", "symbol": "the-open-network", "depot": 4850, "retrait": 4300, "frais": 0.03},
}

@st.cache_data(ttl=300)
def get_prices():
    ids = [v["symbol"] for v in services_info.values() if v["type"] == "crypto"]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd"
    return requests.get(url).json()

try:
    prices = get_prices()
except Exception as e:
    st.error(f"Erreur lors de la récupération des cours en ligne : {e}")
    st.stop()

type_operation = st.radio("Type d'opération :", ["🔁 Dépôt", "🔁 Retrait"])
service = st.selectbox("Choisissez le service :", list(services_info.keys()))
sens = st.radio("Sens de conversion :", ["Ariary ➜ Montant à envoyer", "Montant reçu ➜ Ariary"])

info = services_info[service]
taux = info["depot"] if "Dépôt" in type_operation else info["retrait"]

# Calcul
if sens == "Ariary ➜ Montant à envoyer":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
    montant_usd = montant_ariary / taux

    if info["type"] == "usd":
        frais = info["frais"](montant_usd)
        montant_final = montant_usd - frais
        st.success(f"📤 Montant à envoyer : {montant_final:.2f} USD")
        st.caption(f"Frais appliqués : {frais:.2f} USD")
    else:
        cours = prices[info["symbol"]]["usd"]
        frais = info["frais"]
        montant_crypto = montant_usd / cours
        montant_final = montant_crypto - frais
        st.success(f"📤 Montant à envoyer : {montant_final:.6f} {service}")
        st.caption(f"Frais appliqués : {frais} {service}")

else:
    if info["type"] == "usd":
        montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=1.0)
        montant_ariary = montant_usd * taux
        st.success(f"💵 Montant à recevoir : {montant_ariary:.0f} Ar (Frais inclus)")
    else:
        montant_crypto = st.number_input(f"Montant reçu (en {service})", min_value=0.0, step=0.0001)
        cours = prices[info["symbol"]]["usd"]
        montant_usd = (montant_crypto - info["frais"]) * cours
        montant_ariary = montant_usd * taux
        st.success(f"💵 Montant à recevoir : {montant_ariary:.0f} Ar (Frais inclus)")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Opération": type_operation,
    "Service": service,
    "Taux": taux,
    "Frais": f"{frais:.6f}" if isinstance(frais, float) else frais,
    "Montant (USD/Crypto)": f"{montant_usd:.2f}" if info["type"] == "usd" else f"{montant_final:.6f}",
    "Montant (Ar)": f"{montant_ariary:.0f} Ar"
})

df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter l'historique (CSV)", df.to_csv(index=False).encode(), file_name="historique_261exchange.csv", mime="text/csv")

if st.checkbox("📜 Voir l'historique complet"):
    st.dataframe(df)
