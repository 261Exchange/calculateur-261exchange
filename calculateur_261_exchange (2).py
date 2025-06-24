import streamlit as st

st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")

# Taux personnalisés
taux_depot = 4750
taux_retrait_standard = 4400
taux_retrait_speciaux = 4300
services_speciaux = ["Skrill - USD", "Neteller - USD", "Payeer - USD", "AIRTM - USDC"]

# Tous les services
services = [
    "Skrill - USD", "Neteller - USD", "Payeer - USD", "AIRTM - USDC", "Binance - USDT", "OKX - USDT", "FaucetPay - USDT",
    "Bitget - USDT", "Redotpay - USDT", "Tether TRC20 - USDT", "Cwallet - USDT", "Tether BEP20 - USDT",
    "Bybit - USDT", "MEXC - USDT", "Deriv - USD"
]

# Titre
st.title("📱 261 Exchange – Calculateur Pro")
st.write("Calcule rapidement le solde à envoyer ou recevoir selon le service, le montant, les frais et les taux.")

# Type d'opération
operation = st.selectbox("Type d'opération", ["Dépôt (Ariary ➜ USD)", "Retrait (USD ➜ Ariary)"])

# Service choisi
service = st.selectbox("Service utilisé", services)

# Montant selon l'opération
if operation == "Dépôt (Ariary ➜ USD)":
    montant_ariary = st.number_input("Montant payé par le client (en Ariary)", min_value=0.0, value=0.0, step=100.0)
    marge = st.number_input("Marge appliquée (%)", min_value=0.0, value=0.0, step=0.1)

    taux = taux_depot
    montant_usd = montant_ariary / (taux * (1 + marge / 100))
    frais = 0.0

    if service == "Tether TRC20 - USDT":
        frais = 1.0
        montant_usd -= frais
    elif service in ["Skrill - USD", "Neteller - USD"]:
        if montant_usd > 35:
            frais = montant_usd * 0.0145
        else:
            frais = 0.58
        montant_usd -= frais

    st.subheader("💡 Résultat")
    st.write(f"💸 Montant à envoyer : {montant_usd:.2f} USD")
    st.write(f"🧾 Frais appliqués : {frais:.2f} USD")
    st.write(f"🟢 Bénéfice net estimé : {(montant_ariary / taux) - montant_usd - frais:.2f} USD")

else:
    montant_usd = st.number_input("Montant à remettre au client (en USD)", min_value=0.0, value=0.0, step=1.0)
    taux = taux_retrait_speciaux if service in services_speciaux else taux_retrait_standard
    montant_ariary = montant_usd * taux
    st.subheader("💡 Résultat")
    st.write(f"💰 Montant à recevoir du client : {montant_ariary:,.0f} MGA")
    st.write(f"📌 Taux appliqué : {taux} Ar/USD")
