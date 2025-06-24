import streamlit as st
import requests
import datetime
import pandas as pd

# --- Configuration de la page ---
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.image("https://261exchange.com/logo.png", width=200)
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en Ariary ou en devise selon l'opération.")

# --- Données des services ---
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

autres_services = {
    "Deriv": {"fee": 0, "taux_depot": 4750, "taux_retrait": 4400},
    "Binance": {"fee": 0, "taux_depot": 4750, "taux_retrait": 4400},
    "Skrill": {"fee": "variable", "taux_depot": 4750, "taux_retrait": 4300},
    "Neteller": {"fee": "variable", "taux_depot": 4750, "taux_retrait": 4300},
    "Payeer": {"fee": "variable", "taux_depot": 4750, "taux_retrait": 4300},
    "AIRTM": {"fee": 0, "taux_depot": 4750, "taux_retrait": 4300}
}

# --- Récupération des cours crypto ---
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

# --- Choix du service ---
all_services = list(autres_services.keys()) + list(cryptos.keys())
service = st.selectbox("Choisissez le service :", all_services)
operation = st.radio("Type d'opération :", ["🔁 Dépôt ➜ USD/Crypto", "🔁 Retrait USD/Crypto ➜ Ariary"])

# --- Taux par défaut ---
if service in autres_services:
    taux = autres_services[service]["taux_depot"] if operation.startswith("🔁 Dépôt") else autres_services[service]["taux_retrait"]
else:
    taux = 4850 if operation.startswith("🔁 Dépôt") else 4300
    price_usd = prices[service]["usd"]
    symbol = cryptos[service]["symbol"]
    fee = cryptos[service]["fee"]

# --- Calculs ---
if operation.startswith("🔁 Dépôt"):
    amount_mga = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
    usd_amount = amount_mga / taux

    if service in autres_services:
        frais = 0
        if autres_services[service]["fee"] == "variable":
            frais = 0.58 if usd_amount <= 35 else usd_amount * 0.0145
        final_usd = usd_amount - frais
        st.markdown("### 📊 Résultat")
        st.write(f"✅ Montant à envoyer : **{final_usd:.2f} USD**")
        st.write(f"💸 Frais : {frais:.2f} USD")

    else:
        crypto_amount = usd_amount / price_usd
        final_amount = crypto_amount - fee
        st.markdown("### 📊 Résultat")
        st.write(f"✅ {final_amount:.6f} {symbol} à envoyer")
        st.write(f"💸 Frais : {fee} {symbol}")

else:
    usd_input = st.number_input("Montant en USD à recevoir", min_value=0.0, step=1.0)
    amount_mga = usd_input * taux

    if service in autres_services:
        st.markdown("### 📊 Résultat")
        st.write(f"🪙 À envoyer : **{usd_input:.2f} USD**")
        st.write(f"💰 À recevoir : **{amount_mga:.0f} Ar**")

    else:
        crypto_amount = usd_input / price_usd
        total_with_fee = crypto_amount + fee
        st.markdown("### 📊 Résultat")
        st.write(f"🪙 {total_with_fee:.6f} {symbol} à recevoir")
        st.write(f"💰 Montant total en Ariary : {amount_mga:.0f} Ar")
        st.write(f"🧾 Frais inclus : {fee} {symbol}")

# --- Historique ---
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Type": operation,
    "Service": service,
    "Montant MGA": f"{amount_mga:.0f} Ar",
    "USD ou Crypto": f"{usd_amount:.2f} USD" if service in autres_services else f"{final_amount:.6f} {symbol}",
    "Frais": f"{frais:.2f} USD" if service in autres_services else f"{fee} {symbol}"
})

# --- Export et affichage ---
df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter l'historique (CSV)", df.to_csv(index=False).encode(), file_name="historique_261exchange.csv", mime="text/csv")
if st.checkbox("📜 Voir l'historique complet"):
    st.dataframe(df)
