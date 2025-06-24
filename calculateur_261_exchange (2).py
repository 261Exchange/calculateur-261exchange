import streamlit as st
import requests
import datetime
import pandas as pd

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

# === SERVICES ET CONFIGURATION ===
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

services_fiats = ["Skrill", "Neteller", "Payeer", "AIRTM", "Tether BEP20"]
services_1usd_fee = ["Tether TRC20"]
autres_services = ["OKX", "Binance", "FaucetPay", "Bitget", "Redotpay", "Cwallet", "Bybit", "MEXC", "Deriv"]

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

# === TAUX ===
taux_crypto_depot = 4850
taux_crypto_retrait = 4300
taux_fiat = 4750
taux_fiat_retrait = 4300
taux_autres_retrait = 4400

# === AFFICHER PRIX UNITAIRE CRYPTO ===
st.subheader("🔍 Prix unitaire d’une cryptomonnaie")
selected_crypto = st.selectbox("Choisir une crypto :", list(cryptos.keys()), format_func=lambda x: cryptos[x]["symbol"])
if selected_crypto in prices:
    st.info(f"💲 1 {cryptos[selected_crypto]['symbol']} = {prices[selected_crypto]['usd']} USD")

# === CALCULATEUR PRINCIPAL ===
st.subheader("🔁 Conversion")
operation = st.radio("Type d'opération :", ["Dépôt", "Retrait"])
all_services = services_fiats + services_1usd_fee + list(cryptos.keys()) + autres_services
service = st.selectbox("Service utilisé :", all_services)
sens = st.radio("Sens de conversion :", ["Ariary ➜ USD/Crypto", "USD/Crypto ➜ Ariary"])

is_crypto = service in cryptos
cours = prices[service]["usd"] if is_crypto else None
frais = 0

# === TAUX PAR SERVICE ===
if is_crypto:
    taux = taux_crypto_depot if operation == "Dépôt" else taux_crypto_retrait
    frais = cryptos[service]["fee"]
elif service in services_fiats:
    taux = taux_fiat if operation == "Dépôt" else taux_fiat_retrait
elif service in services_1usd_fee:
    taux = taux_fiat if operation == "Dépôt" else taux_fiat_retrait
    if operation == "Dépôt":
        frais = 1
else:
    taux = taux_fiat if operation == "Dépôt" else taux_autres_retrait

# === CALCULS ===
st.write("---")
result_text = ""
if sens == "Ariary ➜ USD/Crypto":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
    montant_usd = montant_ariary / taux

    if service in ["Skrill", "Neteller"] and operation == "Dépôt":
        frais = 0.58 if montant_usd <= 35 else round(montant_usd * 0.0145, 2)

    if is_crypto:
        montant_crypto = montant_usd / cours
        montant_net = montant_crypto - frais
        st.success(f"🪙 Montant à envoyer : {montant_net:.6f} {cryptos[service]['symbol']}")
        st.write(f"💸 Frais appliqués : {frais} {cryptos[service]['symbol']}")
        result_text = f"{montant_net:.6f} {cryptos[service]['symbol']} | {montant_ariary:.0f} Ar"
    else:
        montant_net = montant_usd - frais
        st.success(f"💵 Montant à envoyer : {montant_net:.2f} USD")
        st.write(f"💸 Frais appliqués : {frais:.2f} USD")
        result_text = f"{montant_net:.2f} USD | {montant_ariary:.0f} Ar"

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

# === BOUTON DE COPIE ===
if result_text:
    st.markdown("### 📋 Copier le résultat")
    st.code(result_text)

# === HISTORIQUE ===
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Opération": operation,
    "Service": service,
    "Résultat": result_text,
    "Frais": f"{frais:.6f}" if isinstance(frais, float) else frais
})

df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter l'historique (CSV)", data=df.to_csv(index=False).encode(), file_name="historique_exchange.csv", mime="text/csv")

if st.checkbox("📜 Voir l'historique complet"):
    st.dataframe(df)
