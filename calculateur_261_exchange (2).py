import streamlit as st
import requests
import datetime
import pandas as pd

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

# Liste des cryptos et frais spécifiques
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

# Récupération des cours CoinGecko
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

# Choix de l’opération
operation = st.radio("Type d'opération :", ["🔁 Dépôt Crypto ➜ USD", "🔁 Retrait USD ➜ Crypto"])
crypto_name = st.selectbox("Choisissez la cryptomonnaie :", list(cryptos.keys()), format_func=lambda x: cryptos[x]["symbol"])
crypto = cryptos[crypto_name]
price_usd = prices[crypto_name]['usd']
fee = crypto["fee"]

# Taux 261 Exchange
taux_depot = 4850
taux_retrait = 4300

# Entrées
if operation == "🔁 Dépôt Crypto ➜ USD":
    amount_mga = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
    usd_amount = amount_mga / taux_depot
    crypto_amount = usd_amount / price_usd
    final_amount = crypto_amount - fee

    st.markdown("### 📊 Résultat")
    st.write(f"✅ {final_amount:.6f} {crypto['symbol']} à envoyer")
    st.write(f"💸 Frais : {fee} {crypto['symbol']}")

else:
    usd_to_send = st.number_input("Montant en USD à envoyer", min_value=0.0, step=1.0)
    amount_mga = usd_to_send * taux_retrait
    crypto_amount = usd_to_send / price_usd
    final_amount = crypto_amount + fee

    st.markdown("### 📊 Résultat")
    st.write(f"🪙 {final_amount:.6f} {crypto['symbol']} à recevoir")
    st.write(f"💰 Montant total en Ariary : {amount_mga:.0f} Ar")
    st.write(f"🧾 Frais inclus : {fee} {crypto['symbol']}")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Type": operation,
    "Crypto": crypto['symbol'],
    "Montant MGA": f"{amount_mga:.0f} Ar",
    "Montant crypto": f"{final_amount:.6f} {crypto['symbol']}",
    "Frais": f"{fee} {crypto['symbol']}"
})

# Export CSV
df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter l'historique (CSV)", df.to_csv(index=False).encode(), file_name="historique_crypto.csv", mime="text/csv")

# Affichage historique
if st.checkbox("📜 Voir l'historique complet"):
    st.dataframe(df)
