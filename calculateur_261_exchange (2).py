import streamlit as st
import requests
import datetime
import pandas as pd

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

cryptos = {
    "tron": {"symbol": "TRX", "fee": 1},
    "bitcoin": {"symbol": "BTC", "fee": 0.00003},
    "ethereum": {"symbol": "ETH", "fee": 0.0004},
    "binancecoin": {"symbol": "BNB", "fee": 0.00009},
    "ripple": {"symbol": "XRP", "fee": 0.2},
    "dogecoin": {"symbol": "DOGE", "fee": 1},
    "solana": {"symbol": "SOL", "fee": 0.001},
    "litecoin": {"symbol": "LTC", "fee": 0.00015},
    "sui": {"symbol": "SUI", "fee": 0.07},
    "the-open-network": {"symbol": "TON", "fee": 0.03}
}

@st.cache_data(ttl=300)
def get_prices():
    ids = ",".join(cryptos.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    res = requests.get(url)
    return res.json()

try:
    prices = get_prices()
except Exception as e:
    st.error(f"Erreur lors de la récupération des cours : {e}")
    st.stop()

taux_crypto_depot = 4850
taux_crypto_retrait = 4300
taux_fiat = 4750
taux_fiat_retrait = 4300
taux_autres_retrait = 4400

st.subheader("🔍 Prix unitaire d’une cryptomonnaie")
selected_crypto = st.selectbox("Choisir une crypto :", list(cryptos.keys()), format_func=lambda x: cryptos[x]["symbol"])
if selected_crypto in prices:
    st.info(f"💲 1 {cryptos[selected_crypto]['symbol']} = {prices[selected_crypto]['usd']} USD")

st.subheader("🔁 Conversion")
operation = st.radio("Type d'opération :", ["Dépôt", "Retrait"])
service = st.selectbox("Service utilisé :", [
    "Skrill", "Neteller", "Payeer", "AIRTM", "Tether BEP20"
] + list(cryptos.keys()) + ["Autre"])
sens = st.radio("Sens de conversion :", ["Ariary ➜ USD/Crypto", "USD/Crypto ➜ Ariary"])

is_crypto = service in cryptos
frais = 0
cours = prices[service]["usd"] if is_crypto else None

if is_crypto:
    taux = taux_crypto_depot if operation == "Dépôt" else taux_crypto_retrait
    frais = cryptos[service]['fee']
elif service in ["Skrill", "Neteller"]:
    taux = taux_fiat if operation == "Dépôt" else taux_fiat_retrait
elif service in ["Payeer", "AIRTM", "Tether BEP20"]:
    taux = taux_fiat if operation == "Dépôt" else taux_fiat_retrait
else:
    taux = taux_fiat if operation == "Dépôt" else taux_autres_retrait

st.write("---")
montant_final = ""
if sens == "Ariary ➜ USD/Crypto":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
    montant_usd = montant_ariary / taux

    if service in ["Skrill", "Neteller"] and operation == "Dépôt":
        frais = 0.58 if montant_usd <= 35 else round(montant_usd * 0.0145, 2)

    if is_crypto:
        montant_crypto = montant_usd / cours
        montant_final = montant_crypto - frais
        st.success(f"🪙 Montant à envoyer : {montant_final:.6f} {cryptos[service]['symbol']}")
        st.write(f"💸 Frais appliqués : {frais} {cryptos[service]['symbol']}")
        result_text = f"{montant_final:.6f} {cryptos[service]['symbol']} | {montant_ariary:.0f} Ar"
    else:
        montant_final = montant_usd - frais
        st.success(f"💵 Montant à envoyer : {montant_final:.2f} USD")
        st.write(f"💸 Frais appliqués : {frais:.2f} USD")
        result_text = f"{montant_final:.2f} USD | {montant_ariary:.0f} Ar"

else:
    if is_crypto:
        montant_crypto = st.number_input(f"Montant à envoyer ({cryptos[service]['symbol']})", min_value=0.0)
        montant_usd = (montant_crypto - frais) * cours
        montant_ariary = montant_usd * taux
        st.success(f"💵 Montant à recevoir : {montant_ariary:.0f} Ar")
        st.write(f"💸 Frais appliqués : {frais} {cryptos[service]['symbol']}")
        result_text = f"{montant_crypto:.6f} {cryptos[service]['symbol']} ➜ {montant_ariary:.0f} Ar"
    else:
        montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0)
        if service in ["Skrill", "Neteller"] and operation == "Dépôt":
            frais = 0.58 if montant_usd <= 35 else round(montant_usd * 0.0145, 2)
        montant_ariary = (montant_usd + frais) * taux
        st.success(f"💵 Montant à recevoir : {montant_ariary:.0f} Ar")
        st.write(f"💸 Frais appliqués : {frais:.2f} USD")
        result_text = f"{montant_usd:.2f} USD ➜ {montant_ariary:.0f} Ar"

# 💾 Bouton pour copier le résultat
if result_text:
    st.markdown("### 📋 Copier le résultat")
    st.code(result_text)

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Opération": operation,
    "Service": service,
    "Résultat": result_text,
    "Frais": f"{frais:.6f} {cryptos[service]['symbol']}" if is_crypto else f"{frais:.2f} USD"
})

df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter l'historique (CSV)", data=df.to_csv(index=False).encode(), file_name="historique_exchange.csv", mime="text/csv")

if st.checkbox("📜 Voir l'historique complet"):
    st.dataframe(df)
