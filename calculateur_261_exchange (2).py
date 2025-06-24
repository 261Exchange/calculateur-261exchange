import streamlit as st
import requests
import datetime
import pandas as pd

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

# Cryptos avec leurs identifiants CoinGecko et frais en crypto
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
    "matic-network": {"symbol": "MATIC", "fee": 1},
    "the-open-network": {"symbol": "TON", "fee": 0.03}
}

# Services fiat classiques
fiat_services = {
    "Skrill", "Neteller", "Payeer", "AIRTM", "Redotpay", "Bybit", "MEXC", "OKX", "Binance", "FaucetPay", "Cwallet", "Tether TRC20", "Tether BEP20"
}

# Taux fixes
taux_depot = 4750
taux_retrait_crypto = 4300
taux_retrait_fiat = 4300

# Récupération des prix crypto en temps réel
@st.cache_data(ttl=300)
def get_prices():
    ids = ",".join(cryptos.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    res = requests.get(url)
    return res.json()

try:
    prices = get_prices()
except Exception as e:
    st.error(f"Erreur de récupération des cours : {e}")
    st.stop()

# Sélection
operation = st.radio("Type d'opération :", ["🔁 Dépôt", "🔁 Retrait"])
all_services = list(cryptos.keys()) + list(fiat_services)
service = st.selectbox("Service utilisé :", all_services)
sens = st.radio("Sens de conversion :", ["Ariary ➜ Montant à envoyer", "Montant reçu ➜ Ariary"])

# Détection crypto ou fiat
is_crypto = service in cryptos

# Affichage résultat
if operation == "🔁 Dépôt":
    taux = taux_depot
    frais = 0 if not is_crypto else cryptos[service]['fee']
elif operation == "🔁 Retrait":
    taux = taux_retrait_crypto if is_crypto else taux_retrait_fiat
    frais = 0  # Pas de frais au retrait

# Calculs
if sens == "Ariary ➜ Montant à envoyer":
    amount_mga = st.number_input("Montant en Ariary", min_value=0.0, step=1000.0)
    amount_usd = amount_mga / taux
    if is_crypto:
        price_usd = prices[service]["usd"]
        crypto_amount = amount_usd / price_usd
        montant_final = crypto_amount - frais
        st.success(f"✅ {montant_final:.6f} {cryptos[service]['symbol']} à envoyer")
        st.write(f"💸 Frais : {frais} {cryptos[service]['symbol']}")
    else:
        montant_final = amount_usd
        st.success(f"✅ {montant_final:.2f} USD à envoyer (Frais inclus)")

else:
    if is_crypto:
        crypto_amount = st.number_input("Montant à envoyer (en crypto)", min_value=0.0, step=0.0001)
        amount_usd = (crypto_amount - frais) * prices[service]["usd"]
        amount_mga = amount_usd * taux
        st.success(f"💵 Montant à recevoir : {amount_mga:.0f} Ar")
        st.write(f"🔸 Frais : {frais} {cryptos[service]['symbol']}")
    else:
        usd_amount = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=1.0)
        amount_mga = usd_amount * taux
        st.success(f"💵 Montant à recevoir : {amount_mga:.0f} Ar (Frais inclus)")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Service": service,
    "Opération": operation,
    "Sens": sens,
    "Frais": f"{frais} {cryptos[service]['symbol']}" if is_crypto else "0 USD",
    "Montant MGA": f"{amount_mga:.0f} Ar" if sens == "Montant reçu ➜ Ariary" else f"{amount_mga:.0f} Ar",
    "Montant envoyé": f"{montant_final:.6f} {cryptos[service]['symbol']}" if is_crypto else f"{montant_final:.2f} USD"
})

# Export CSV
df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter l'historique (CSV)", df.to_csv(index=False).encode(), file_name="historique_261.csv", mime="text/csv")

if st.checkbox("📜 Voir l'historique complet"):
    st.dataframe(df)
