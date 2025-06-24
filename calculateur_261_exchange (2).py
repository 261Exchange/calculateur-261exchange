import streamlit as st
import datetime
import pandas as pd

# Logo
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")
st.image("https://261exchange.com/logo.png", width=200)  # Change cette URL par celle de ton logo si besoin

st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calcule rapidement le montant à envoyer ou à recevoir selon le taux, les frais et le sens de conversion.")

# Historique de session
if "historique" not in st.session_state:
    st.session_state.historique = []

# Champs
operation = st.selectbox("Type d'opération :", ["Dépôt (4750 Ar/USD)", "Retrait (4400 Ar/USD sauf 4300 Ar)"])
service = st.selectbox("Service utilisé :", [
    "Deriv", "Skrill", "Neteller", "Payeer", "AIRTM", "Binance", "OKX", "FaucetPay", "Bitget", "Redotpay", 
    "Tether TRC20", "Cwallet", "Tether BEP20", "Bybit", "MEXC"
])

sens = st.radio("Choisir la direction du calcul :", ["🔁 Ariary ➜ USD", "🔁 USD ➜ Ariary"])
if sens == "🔁 Ariary ➜ USD":
    montant_ariary = st.number_input("Montant payé par le client (en Ariary)", min_value=0.0, step=1000.0)
else:
    montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=0.01)

# Taux selon opération
if operation.startswith("Dépôt"):
    taux =
