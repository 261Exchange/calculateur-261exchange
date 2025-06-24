import streamlit as st
import requests
import datetime
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto, en USD ou en Ariary selon l'opération.")

# Taux
TAUX_DEPOT = 4850
TAUX_RETRAIT = 4300

# Services fiat avec frais conditionnels
services_fiat = {
    "Skrill": {"fee_mode": "usd", "fee_fixed": 0.58, "fee_percent": 0.0145, "seuil": 35},
    "Neteller": {"fee_mode": "usd", "fee_fixed": 0.58, "fee_percent": 0.0145, "seuil": 35},
    "Payeer": {"fee_mode": "usd", "fee_fixed": 0.58, "fee_percent": 0.0145, "seuil": 35},
    "AIRTM": {"fee_mode": "usd", "fee_fixed": 0.00, "fee_percent": 0.00, "seuil": 0},
}

# Cryptos avec frais fixes
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

# Récupérer les prix crypto en USD
@st.cache_data(ttl=300)
def get_crypto_prices():
    ids = ",".join(cryptos.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    res = requests.get(url)
    return res.json()

try:
    crypto_prices = get_crypto_prices()
except Exception as e:
    st.error(f"Erreur récupération des cours : {e}")
    st.stop()

# Sélection de service
type_service = st.radio("Type de service :", ["Crypto", "Fiat"])

if type_service == "Crypto":
    crypto_name = st.selectbox("Cryptomonnaie :", list(cryptos.keys()), format_func=lambda x: cryptos[x]["symbol"])
    service = cryptos[crypto_name]
    cours_usd = crypto_prices[crypto_name]["usd"]
    operation = st.radio("Opération :", ["Dépôt Ariary ➜ Crypto", "Retrait Crypto ➜ Ariary"])

    if operation == "Dépôt Ariary ➜ Crypto":
        montant_mga = st.number_input("Montant en Ariary", min_value=0.0, step=1000.0)
        montant_usd = montant_mga / TAUX_DEPOT
        montant_crypto = montant_usd / cours_usd
        montant_net = montant_crypto - service["fee"]
        st.markdown("### Résultat")
        st.write(f"✅ À envoyer : {montant_net:.6f} {service['symbol']}")
        st.write(f"💸 Frais fixe : {service['fee']} {service['symbol']}")

    else:
        montant_crypto = st.number_input("Montant en crypto", min_value=0.0, step=0.0001)
        montant_usd = montant_crypto * cours_usd
        montant_mga = montant_usd * TAUX_RETRAIT
        st.markdown("### Résultat")
        st.write(f"💰 Total en Ariary : {montant_mga:.0f} Ar")
        st.write(f"🪙 Montant envoyé : {montant_crypto:.6f} {service['symbol']}")
        st.write(f"💸 Frais inclus : {service['fee']} {service['symbol']}")

else:
    fiat_name = st.selectbox("Service :", list(services_fiat.keys()))
    service = services_fiat[fiat_name]
    operation = st.radio("Opération :", ["Dépôt Ariary ➜ USD", "Retrait USD ➜ Ariary"])

    if operation == "Dépôt Ariary ➜ USD":
        montant_mga = st.number_input("Montant en Ariary", min_value=0.0, step=1000.0)
        montant_usd_brut = montant_mga / TAUX_DEPOT
        if montant_usd_brut <= service["seuil"]:
            frais = service["fee_fixed"]
        else:
            frais = montant_usd_brut * service["fee_percent"]
        montant_net = montant_usd_brut - frais
        st.markdown("### Résultat")
        st.write(f"✅ À envoyer : {montant_net:.2f} USD")
        st.write(f"💸 Frais appliqués : {frais:.2f} USD")

    else:
        montant_usd = st.number_input("Montant en USD", min_value=0.0, step=1.0)
        montant_mga = montant_usd * TAUX_RETRAIT
        st.markdown("### Résultat")
        st.write(f"💰 Montant à recevoir : {montant_mga:.0f} Ar")
        st.write(f"✅ Montant envoyé : {montant_usd:.2f} USD")
        st.write("💸 Aucun frais pour le retrait")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Type": operation,
    "Service": crypto_name if type_service == "Crypto" else fiat_name,
    "Montant MGA": f"{montant_mga:.0f} Ar" if 'montant_mga' in locals() else "-",
    "Montant USD": f"{montant_usd:.2f} USD" if 'montant_usd' in locals() else "-",
    "Montant crypto": f"{montant_net:.6f} {cryptos[crypto_name]['symbol']}" if type_service == "Crypto" and operation == "Dépôt Ariary ➜ Crypto" else "-"
})

# Export
df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter l'historique (CSV)", df.to_csv(index=False).encode(), file_name="historique_261.csv", mime="text/csv")
if st.checkbox("📜 Voir l'historique complet"):
    st.dataframe(df)
