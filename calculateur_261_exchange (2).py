import streamlit as st
import requests
import datetime
import pandas as pd

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant à envoyer ou à recevoir selon le service, les frais et le taux en vigueur.")

# Cryptomonnaies avec frais
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
    "the-open-network": {"symbol": "TON", "fee": 0.03},
    "matic-network": {"symbol": "MATIC", "fee": 1}
}

# Services fiat et autres
autres_services = {
    "Skrill": {"frais_fixe": 0.58, "pourcentage": 0.0145},
    "Neteller": {"frais_fixe": 0.58, "pourcentage": 0.0145},
    "Payeer": {"frais_fixe": 0.0, "pourcentage": 0.0},
    "AIRTM": {"frais_fixe": 0.0, "pourcentage": 0.0},
    "Tether BEP20": {"frais_fixe": 0.0, "pourcentage": 0.0},
    "Tether TRC20": {"frais_fixe": 1.0, "pourcentage": 0.0}
}

# Obtenir les cours crypto
@st.cache_data(ttl=300)
def get_prices():
    ids = ",".join(cryptos.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    return requests.get(url).json()

try:
    prices = get_prices()
except Exception as e:
    st.error(f"Erreur récupération des cours : {e}")
    st.stop()

# Interface
all_services = list(cryptos.keys()) + list(autres_services.keys()) + ["Autres"]
operation = st.radio("Type d'opération :", ["🔁 Dépôt", "🔁 Retrait"])
service = st.selectbox("Service :", all_services)

# Taux selon catégorie
if service in cryptos:
    taux = 4850 if operation == "🔁 Dépôt" else 4300
elif service in autres_services:
    taux = 4750 if operation == "🔁 Dépôt" else 4300
else:
    taux = 4750 if operation == "🔁 Dépôt" else 4400

sens = st.radio("Conversion :", ["Ariary ➜ USD/Crypto", "USD/Crypto ➜ Ariary"])

# Entrée et calcul
montant_mga, montant_resultat, frais = 0, 0, 0

if sens == "Ariary ➜ USD/Crypto":
    montant_mga = st.number_input("Montant en Ariary", min_value=0.0, step=1000.0)
    usd = montant_mga / taux

    if service in cryptos:
        cours = prices[service]['usd']
        frais = cryptos[service]['fee']
        montant_resultat = usd / cours - frais
        st.success(f"💸 {montant_resultat:.6f} {cryptos[service]['symbol']} à envoyer (Frais : {frais} {cryptos[service]['symbol']})")
    elif service in autres_services:
        frais = autres_services[service]['frais_fixe'] if usd <= 35 else usd * autres_services[service]['pourcentage']
        montant_resultat = usd - frais
        st.success(f"💸 {montant_resultat:.2f} USD à envoyer (Frais : {frais:.2f} USD)")
    else:
        montant_resultat = usd
        st.success(f"💸 {montant_resultat:.2f} USD à envoyer (Pas de frais)")
else:
    montant = st.number_input("Montant à envoyer (USD ou Crypto)", min_value=0.0, step=1.0)

    if service in cryptos:
        cours = prices[service]['usd']
        frais = cryptos[service]['fee']
        montant_resultat = (montant + frais) * cours * taux
        st.success(f"💰 {montant_resultat:.0f} Ar à recevoir (Frais : {frais} {cryptos[service]['symbol']})")
    elif service in autres_services:
        montant_resultat = montant * taux
        st.success(f"💰 {montant_resultat:.0f} Ar à recevoir (Aucun frais)")
    else:
        montant_resultat = montant * taux
        st.success(f"💰 {montant_resultat:.0f} Ar à recevoir (Taux par défaut)")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Opération": operation,
    "Service": service,
    "Montant MGA": f"{montant_mga:.0f} Ar" if montant_mga else "",
    "Résultat": f"{montant_resultat:.2f}",
    "Frais": f"{frais}"
})

df = pd.DataFrame(st.session_state.historique)

st.download_button("⬇️ Exporter l'historique (CSV)", df.to_csv(index=False).encode(), file_name="historique_261exchange.csv", mime="text/csv")

if st.checkbox("📜 Voir l’historique"):
    st.dataframe(df)
