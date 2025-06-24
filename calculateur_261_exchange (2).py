import streamlit as st
import requests

# Configuration de la page
st.set_page_config(page_title="261 Exchange – Estimation Swapzone", layout="centered")

st.title("🔁 Estimation d'Échange Crypto avec Swapzone")
st.write("Comparez les montants estimés d’échange entre deux cryptomonnaies via Swapzone.")

# Clé API Swapzone (à sécuriser idéalement)
API_KEY = "ZWFPXI5ht"

# Liste des cryptos supportées (simplifiée)
cryptos = [
    "btc", "eth", "usdt", "bnb", "trx", "ltc", "xrp", "doge", "matic", "shib"
]

# Sélection utilisateur
from_coin = st.selectbox("Depuis :", cryptos, index=0)
to_coin = st.selectbox("Vers :", cryptos, index=1)
amount = st.number_input(f"Montant de {from_coin.upper()} :", min_value=0.0001, value=0.01, step=0.0001, format="%.8f")

# Estimation
if st.button("🔍 Estimer"):
    url = "https://api.swapzone.io/v1/exchange/estimated"
    params = {
        "from": from_coin,
        "to": to_coin,
        "amount": amount,
        "apiKey": API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "estimatedAmount" in data:
            st.success(f"✅ Vous recevrez environ **{data['estimatedAmount']} {to_coin.upper()}** pour {amount} {from_coin.upper()}.")
            st.write(f"💱 Taux estimé : 1 {from_coin.upper()} ≈ {float(data['estimatedAmount'])/amount:.6f} {to_coin.upper()}")
        else:
            st.error("Échec de l’estimation. Vérifiez les crypto ou réessayez plus tard.")
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur d’appel API : {e}")

# Lien de parrainage
st.markdown("---")
st.markdown("🔗 [Échanger maintenant via Swapzone (lien partenaire)](https://swapzone.io/?refId=iIJM3MAWGR)")
