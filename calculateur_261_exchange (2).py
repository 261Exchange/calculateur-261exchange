import streamlit as st
import requests
import datetime
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon l'opération.")

# --- Liste des cryptos supportées ---
cryptos = ["TRX", "BNB", "BTC", "ETH", "TON", "LTC"]

# --- Fonction : récupérer les prix via l'API Binance ---
@st.cache_data(ttl=300)
def get_binance_prices(symbols):
    prices = {}
    try:
        for sym in symbols:
            pair = f"{sym.upper()}USDT"
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            prices[sym.upper()] = float(data['price'])
    except Exception as e:
        st.error(f"Erreur de récupération des cours : {e}")
    return prices

# --- Récupération des cours en USDT ---
cours = get_binance_prices(cryptos)

# --- Historique de session ---
if "historique" not in st.session_state:
    st.session_state.historique = []

# --- Formulaire ---
operation = st.selectbox("Type d'opération :", ["Dépôt (4750 Ar/USD)", "Retrait (4300 Ar/USD)", "Retrait Crypto (4300 Ar/USD)"])
service = st.selectbox("Service utilisé :", ["Skrill", "Neteller", "Payeer", "Binance", "Deriv", "Crypto (TRX, BNB, BTC, etc.)"])

sens = st.radio("Sens de conversion :", ["🔁 Ariary ➜ USD ou Crypto", "🔁 USD ou Crypto ➜ Ariary"])

# --- Entrées utilisateur ---
montant_ariary = 0
montant_usd = 0

if sens == "🔁 Ariary ➜ USD ou Crypto":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
else:
    montant_usd = st.number_input("Montant à envoyer (en USD ou Crypto)", min_value=0.0, step=0.01)

# --- Déterminer le taux et les frais ---
if operation.startswith("Dépôt"):
    taux = 4750
    frais = 0.0
    if service in ["Skrill", "Neteller", "Payeer"]:
        if sens == "🔁 Ariary ➜ USD ou Crypto" and montant_ariary / taux <= 35:
            frais = 0.58
        else:
            frais = (montant_ariary * 0.0145 / taux) if sens.startswith("🔁 Ariary") else (montant_usd * 0.0145)
    elif service == "Crypto (TRX, BNB, BTC, etc.)":
        frais = 1.0  # fixe par transaction
elif operation == "Retrait (4300 Ar/USD)":
    taux = 4300
    frais = 0.0
elif operation == "Retrait Crypto (4300 Ar/USD)":
    taux = 4300
    frais = 0.0

# --- Choix de la crypto ---
crypto_choisie = None
if service == "Crypto (TRX, BNB, BTC, etc.)":
    crypto_choisie = st.selectbox("Choisissez la crypto :", cryptos)
    prix_crypto = cours.get(crypto_choisie.upper(), 0)
    if prix_crypto == 0:
        st.error(f"Erreur : prix introuvable pour {crypto_choisie}")
        st.stop()
else:
    prix_crypto = 1  # cas USD

# --- Calculs ---
if sens == "🔁 Ariary ➜ USD ou Crypto":
    montant_usd_brut = montant_ariary / taux
    montant_net_usd = montant_usd_brut - frais
    montant_en_crypto = montant_net_usd / prix_crypto
else:
    montant_usd_total = montant_usd + frais
    montant_ariary = montant_usd_total * taux
    montant_en_crypto = montant_usd / prix_crypto

# --- Affichage des résultats ---
st.markdown("### 💡 Résultat")
if service == "Crypto (TRX, BNB, BTC, etc.)":
    st.write(f"📤 Montant à envoyer : **{montant_en_crypto:.6f} {crypto_choisie}**")
    st.write(f"🔸 Prix du {crypto_choisie} : {prix_crypto:.3f} USD")
    st.write(f"🔸 Frais appliqués : **{frais:.2f} USD**")
else:
    st.write(f"📤 Montant à envoyer : **{montant_usd:.2f} USD**")
    st.write(f"🔸 Frais appliqués : **{frais:.2f} USD**")

if sens.startswith("🔁 USD ou Crypto ➜ Ariary"):
    st.write(f"💵 Montant à recevoir : **{montant_ariary:.0f} Ar**")

# --- Historique ---
now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Service": service,
    "Opération": operation,
    "Montant MGA": f"{montant_ariary:.0f} Ar",
    "Montant USD ou Crypto": f"{montant_usd:.2f} USD" if not crypto_choisie else f"{montant_en_crypto:.6f} {crypto_choisie}",
    "Frais": f"{frais:.2f} USD"
})

df = pd.DataFrame(st.session_state.historique)
if st.button("📋 Copier le dernier résultat"):
    st.code(df.iloc[-1].to_string(), language='text')

st.download_button("⬇️ Exporter CSV", data=df.to_csv(index=False).encode(), file_name="historique_261_exchange.csv", mime="text/csv")

if st.checkbox("📜 Voir l'historique complet"):
    st.dataframe(df)
