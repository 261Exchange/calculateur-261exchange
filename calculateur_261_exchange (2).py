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

# === FONCTION POUR OBTENIR LES COURS ACTUELS EN USD ===
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
        "Polygone": "polygon",
        "Toncoin": "the-open-network"
    }
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids.values())}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return {name: data[coingecko_id]['usd'] for name, coingecko_id in ids.items()}

# === FRAIS FIXES PAR CRYPTO ===
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
    "Polygone": 1,
    "Toncoin": 0.03
}

crypto_list = list(crypto_frais.keys())

# === RÉCUPÉRER LES COURS EN TEMPS RÉEL ===
try:
    cours_crypto_usd = get_cours_cryptos()
except Exception as e:
    st.error("Erreur lors de la récupération des cours en ligne : " + str(e))
    st.stop()

# === CONSTANTES ===
taux_depot = 4850
taux_retrait = 4300

# === INTERFACE UTILISATEUR ===
operation = st.selectbox("Type d'opération :", ["Dépôt", "Retrait"])
service = st.selectbox("Service utilisé :", crypto_list)
sens = st.radio("Sens de conversion :", ["Ariary ➜ Crypto", "Crypto ➜ Ariary"])

cours_usd = cours_crypto_usd[service]
frais_crypto = crypto_frais[service]
taux = taux_depot if operation == "Dépôt" else taux_retrait

# === CALCULS ===
if sens == "Ariary ➜ Crypto":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
    montant_usd = montant_ariary / taux
    montant_brut = montant_usd / cours_usd
    montant_net = montant_brut - frais_crypto
    st.markdown("### 💡 Résultat")
    st.write(f"🪙 Montant à envoyer : **{montant_net:.6f} {service}**")
    st.write(f"🔸 Frais : **{frais_crypto:.6f} {service}**")
    st.write(f"💵 Équivalent en Ariary : **{montant_ariary:.0f} Ar**")
else:
    montant_crypto = st.number_input("Montant à envoyer (en Crypto)", min_value=0.0, step=0.0001)
    montant_usd = (montant_crypto - frais_crypto) * cours_usd
    montant_ariary = montant_usd * taux
    st.markdown("### 💡 Résultat")
    st.write(f"🪙 Montant reçu : **{montant_crypto:.6f} {service}**")
    st.write(f"🔸 Frais déduits : **{frais_crypto:.6f} {service}**")
    st.write(f"💵 Montant à recevoir : **{montant_ariary:.0f} Ar**")

# === AJOUT À L'HISTORIQUE ===
now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Opération": operation,
    "Service": service,
    "Frais": f"{frais_crypto:.6f} {service}",
    "Crypto": f"{montant_net:.6f} {service}" if sens == "Ariary ➜ Crypto" else f"{montant_crypto:.6f} {service}",
    "Ariary": f"{montant_ariary:.0f} Ar"
})

df = pd.DataFrame(st.session_state.historique)

# === EXPORTATION & AFFICHAGE ===
if st.button("📋 Copier le résultat"):
    st.code(f"{montant_net:.6f} {service} | {montant_ariary:.0f} Ar", language='text')

st.download_button("⬇️ Exporter CSV", data=df.to_csv().encode(), file_name="historique_261_exchange.csv", mime="text/csv")

if st.checkbox("📜 Voir l'historique de session"):
    st.dataframe(df)
