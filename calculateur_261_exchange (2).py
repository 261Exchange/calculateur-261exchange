import streamlit as st
import requests
import datetime
import pandas as pd

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.image("https://261exchange.com/logo.png", width=200)
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

# Cryptomonnaies avec frais spécifiques
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

# Services FIAT
services_fiat = {
    "Skrill": {"fee_fixed": 0.58, "fee_percent": 0.0145, "seuil": 35},
    "Neteller": {"fee_fixed": 0.58, "fee_percent": 0.0145, "seuil": 35},
    "Payeer": {"fee_fixed": 0.58, "fee_percent": 0.0145, "seuil": 35},
    "AIRTM": {"fee_fixed": 0.00, "fee_percent": 0.00, "seuil": 0}
}

# Taux d'échange
taux_depot = 4850
taux_retrait = 4300

# Récupération cours crypto (CoinGecko)
@st.cache_data(ttl=300)
def get_prices():
    ids = ",".join(cryptos.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    res = requests.get(url)
    return res.json()

try:
    prices = get_prices()
except Exception as e:
    st.error(f"Erreur récupération des cours : {e}")
    st.stop()

# Choix du type de service
service_type = st.radio("Choisissez le type de service :", ["🔹 Crypto", "💵 Services Fiat"])

# Choix des options selon le type
if service_type == "🔹 Crypto":
    crypto_name = st.selectbox("Cryptomonnaie :", list(cryptos.keys()), format_func=lambda x: cryptos[x]["symbol"])
    crypto = cryptos[crypto_name]
    price_usd = prices[crypto_name]['usd']
    fee = crypto["fee"]
    operation = st.radio("Opération :", ["🔁 Dépôt (4850 Ar/USD)", "🔁 Retrait (4300 Ar/USD)"])

    if operation == "🔁 Dépôt (4850 Ar/USD)":
        ar_input = st.number_input("Montant payé (Ariary)", min_value=0.0, step=1000.0)
        usd_amount = ar_input / taux_depot
        amount_crypto = usd_amount / price_usd
        amount_final = amount_crypto - fee
        st.markdown("### 📊 Résultat")
        st.write(f"🔹 Montant à envoyer : **{amount_final:.6f} {crypto['symbol']}**")
        st.write(f"🔸 Frais appliqués : {fee} {crypto['symbol']}")
        st.write(f"💰 Montant total en Ariary : {ar_input:.0f} Ar")

    else:
        crypto_input = st.number_input(f"Montant à envoyer (en {crypto['symbol']})", min_value=0.0, step=0.0001)
        usd_amount = (crypto_input - fee) * price_usd
        ar_amount = usd_amount * taux_retrait
        st.markdown("### 📊 Résultat")
        st.write(f"🔹 Montant à recevoir : **{ar_amount:.0f} Ar**")
        st.write(f"🔸 Frais déduits : {fee} {crypto['symbol']}")

else:
    service_name = st.selectbox("Service :", list(services_fiat.keys()))
    service = services_fiat[service_name]
    operation = st.radio("Opération :", ["🔁 Dépôt (4850 Ar/USD)", "🔁 Retrait (4300 Ar/USD)"])

    if operation == "🔁 Dépôt (4850 Ar/USD)":
        ar_input = st.number_input("Montant payé (Ariary)", min_value=0.0, step=1000.0)
        usd_brut = ar_input / taux_depot
        if usd_brut <= service["seuil"]:
            frais = service["fee_fixed"]
        else:
            frais = usd_brut * service["fee_percent"]
        usd_final = usd_brut - frais
        st.markdown("### 📊 Résultat")
        st.write(f"💲 Montant à envoyer : **{usd_final:.2f} USD**")
        st.write(f"🔸 Frais appliqués : {frais:.2f} USD")
        st.write(f"💰 Montant payé : {ar_input:.0f} Ar")

    else:
        usd_input = st.number_input("Montant à envoyer (USD)", min_value=0.0, step=1.0)
        ar_amount = usd_input * taux_retrait
        st.markdown("### 📊 Résultat")
        st.write(f"💰 Montant à recevoir : **{ar_amount:.0f} Ar**")
        st.write(f"✅ Aucuns frais appliqués")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Type": service_type,
    "Service": crypto["symbol"] if service_type == "🔹 Crypto" else service_name,
    "Montant MGA": f"{ar_input:.0f} Ar" if service_type == "🔹 Crypto" or operation == "🔁 Dépôt (4850 Ar/USD)" else f"{ar_amount:.0f} Ar",
    "Montant Final": f"{amount_final:.6f}" if service_type == "🔹 Crypto" and operation == "🔁 Dépôt (4850 Ar/USD)" else (
        f"{ar_amount:.0f} Ar" if service_type == "🔹 Crypto" else f"{usd_final:.2f} USD" if operation == "🔁 Dépôt (4850 Ar/USD)" else f"{ar_amount:.0f} Ar"
    ),
    "Frais": f"{fee} {crypto['symbol']}" if service_type == "🔹 Crypto" else f"{frais:.2f} USD" if operation == "🔁 Dépôt (4850 Ar/USD)" else "0"
})

# Export et affichage
df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter l'historique (CSV)", df.to_csv(index=False).encode(), file_name="historique_261_exchange.csv", mime="text/csv")
if st.checkbox("📜 Voir l'historique complet"):
    st.dataframe(df)
