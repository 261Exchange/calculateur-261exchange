import streamlit as st
import datetime
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")

# Logo
st.image("https://261exchange.com/logo.png", width=200)

st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calcule le montant à envoyer ou à recevoir selon le taux et les frais appliqués.")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

# Formulaire
operation = st.selectbox("Type d'opération :", ["Dépôt (4750 Ar/USD)", "Retrait (4400 Ar/USD sauf 4300 Ar)"])
service = st.selectbox("Service utilisé :", [
    "Deriv", "Skrill", "Neteller", "Payeer", "AIRTM", "Binance", "OKX", "FaucetPay", "Bitget",
    "Redotpay", "Tether TRC20", "Cwallet", "Tether BEP20", "Bybit", "MEXC",
    "Tron", "BNB", "ETH", "BTC", "XRP", "SOL", "Doge", "LTC", "SUI", "Polygone", "Toncoin"
])
sens = st.radio("Sens de conversion :", ["🔁 Ariary ➜ USD", "🔁 USD ➜ Ariary"])

# Saisie utilisateur
montant_ariary = 0
montant_usd = 0

if sens == "🔁 Ariary ➜ USD":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
else:
    montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=0.01)

# Frais crypto (en crypto native)
crypto_frais = {
    "Tron": "1 TRX",
    "BNB": "0.00009 BNB",
    "ETH": "0.0004 ETH",
    "BTC": "0.00003 BTC",
    "XRP": "0.2 XRP",
    "SOL": "0.001 SOL",
    "Doge": "1 DOGE",
    "LTC": "0.00015 LTC",
    "SUI": "0.07 SUI",
    "Polygone": "1 POL",
    "Toncoin": "0.03 TON"
}
crypto_frais_valeurs = {
    "Tron": 1,
    "BNB": 0.00009,
    "ETH": 0.0004,
    "BTC": 0.00003,
    "XRP": 0.2,
    "SOL": 0.001,
    "Doge": 1,
    "LTC": 0.00015,
    "SUI": 0.07,
    "Polygone": 1,
    "Toncoin": 0.03
}
crypto_list = list(crypto_frais.keys())

# Taux & frais
if operation.startswith("Dépôt"):
    if service in crypto_list:
        taux = 4850
        frais_affiche = crypto_frais[service]
        frais_val = 0.0  # Ne pas déduire en USD
    else:
        taux = 4750
        frais_affiche = "0 USD"
        if service in ["Skrill", "Neteller", "Payeer"]:
            if sens == "🔁 Ariary ➜ USD" and montant_ariary / taux <= 35:
                frais_val = 0.58
            else:
                frais_val = (montant_ariary * 0.0145 / taux) if sens == "🔁 Ariary ➜ USD" else (montant_usd * 0.0145)
            frais_affiche = f"{frais_val:.2f} USD"
        elif service == "Tether TRC20":
            frais_val = 1.00
            frais_affiche = "1.00 USD"
        else:
            frais_val = 0.0
else:
    taux = 4300 if service in ["Skrill", "Neteller", "Payeer", "AIRTM"] else 4400
    frais_val = 0.0
    frais_affiche = "0 USD"

# Calculs
if sens == "🔁 Ariary ➜ USD":
    montant_usd_brut = montant_ariary / taux
    montant_final = montant_usd_brut - frais_val
else:
    montant_ariary = (montant_usd + frais_val) * taux
    montant_final = montant_usd

# Affichage des résultats
st.markdown("### 💡 Résultat")
st.write(f"📤 Montant à envoyer : **{montant_final:.6f} USD**")
st.write(f"🔸 Frais appliqués : **{frais_affiche}**")
if service in crypto_list:
    st.info(f"Le frais est appliqué en crypto et **non déduit** ici.")
if sens == "🔁 USD ➜ Ariary":
    st.write(f"💵 Montant à recevoir : **{montant_ariary:.0f} Ar**")

# Historique
now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Opération": operation,
    "Service": service,
    "Montant MGA": f"{montant_ariary:.0f} Ar",
    "Montant USD": f"{montant_final:.6f} USD",
    "Frais": frais_affiche
})

# Copier ou exporter
if st.button("📋 Copier le résultat"):
    st.code(f"{montant_final:.6f} USD | {montant_ariary:.0f} Ar", language='text')

df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter CSV", data=df.to_csv().encode(), file_name="historique_261_exchange.csv", mime="text/csv")

# Affichage historique
if st.checkbox("📜 Voir l'historique de session"):
    st.dataframe(df)
