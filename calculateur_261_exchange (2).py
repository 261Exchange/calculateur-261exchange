import streamlit as st
import datetime
import pandas as pd
import requests

# === CONFIGURATION DE LA PAGE ===
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.image("https://261exchange.com/logo.png", width=200)
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

# === HISTORIQUE DE SESSION ===
if "historique" not in st.session_state:
    st.session_state.historique = []

# === COURS DES CRYPTOS ===
@st.cache_data(ttl=300)
def get_cours_cryptos():
    ids = {
        "Tron": "tron",
        "BNB": "binancecoin",
        "ETH": "ethereum",
        "BTC": "bitcoin",
        "XRP": "ripple",
        "SOL": "solana",
        "Doge": "dogecoin",
        "LTC": "litecoin",
        "SUI": "sui",
        "Polygon": "polygon",
        "Toncoin": "the-open-network"
    }
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids.values())}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return {name: data[coingecko_id]['usd'] for name, coingecko_id in ids.items()}

# === FRAIS FIXES ===
crypto_frais = {
    "Tron": 1,
    "BNB": 0.00009,
    "ETH": 0.0004,
    "BTC": 0.00003,
    "XRP": 0.2,
    "SOL": 0.001,
    "Doge": 1,
    "LTC": 0.00015,
    "SUI": 0.07,
    "Polygon": 1,
    "Toncoin": 0.03
}
crypto_list = list(crypto_frais.keys())

# === RÉCUPÉRATION COURS ===
try:
    cours_crypto_usd = get_cours_cryptos()
except Exception as e:
    st.error("Erreur lors de la récupération des cours en ligne : " + str(e))
    st.stop()

# === TAUX FIXES 261 Exchange ===
taux_depot = 4850
taux_retrait = 4300

# === INTERFACE UTILISATEUR ===
operation = st.selectbox("Type d'opération :", ["Dépôt", "Retrait"])
service = st.selectbox("Crypto utilisée :", crypto_list)
sens = st.radio("Sens de conversion :", ["Ariary ➜ Crypto", "Crypto ➜ Ariary"])

cours_usd = cours_crypto_usd[service]
frais = crypto_frais[service]
taux = taux_depot if operation == "Dépôt" else taux_retrait

# === CALCULS ===
if sens == "Ariary ➜ Crypto":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
    montant_usd = montant_ariary / taux
    montant_brut = montant_usd / cours_usd
    montant_net = montant_brut - frais
    st.markdown("### 💡 Résultat")
    st.write(f"🪙 Montant à envoyer : **{montant_net:.6f} {service}**")
    st.write(f"🔸 Frais : **{frais:.6f} {service}**")
    st.write(f"💵 Équivalent payé : **{montant_ariary:.0f} Ar**")
else:
    montant_crypto = st.number_input("Montant à envoyer (en Crypto)", min_value=0.0, step=0.0001)
    montant_usd = (montant_crypto - frais) * cours_usd
    montant_ariary = montant_usd * taux
    st.markdown("### 💡 Résultat")
    st.write(f"🪙 Montant envoyé : **{montant_crypto:.6f} {service}**")
    st.write(f"🔸 Frais déduits : **{frais:.6f} {service}**")
    st.write(f"💵 Montant reçu : **{montant_ariary:.0f} Ar**")

# === AJOUT HISTORIQUE ===
now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Opération": operation,
    "Sens": sens,
    "Service": service,
    "Frais": f"{frais:.6f} {service}",
    "Crypto": f"{montant_net:.6f} {service}" if sens == "Ariary ➜ Crypto" else f"{montant_crypto:.6f} {service}",
    "Ariary": f"{montant_ariary:.0f} Ar"
})

# === EXPORTATION & AFFICHAGE ===
df = pd.DataFrame(st.session_state.historique)
if st.button("📋 Copier le résultat"):
    res = f"{montant_net:.6f} {service} | {montant_ariary:.0f} Ar" if sens == "Ariary ➜ Crypto" else f"{montant_crypto:.6f} {service} | {montant_ariary:.0f} Ar"
    st.code(res, language='text')

st.download_button("⬇️ Exporter l'historique", data=df.to_csv(index=False).encode(), file_name="historique_261_exchange.csv", mime="text/csv")

if st.checkbox("📜 Voir l'historique de session"):
    st.dataframe(df)
