import streamlit as st
import datetime
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")

# Logo (remplace l'URL si besoin)
st.image("https://261exchange.com/logo.png", width=200)

st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calcule rapidement le montant à envoyer ou à recevoir selon le taux, les frais et le sens de conversion.")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

# Formulaire
operation = st.selectbox("Type d'opération :", ["Dépôt (4750 Ar/USD)", "Retrait (4400 Ar/USD sauf 4300 Ar)"])
service = st.selectbox("Service utilisé :", [
    "Deriv", "Skrill", "Neteller", "Payeer", "AIRTM", "Binance", "OKX", "FaucetPay", "Bitget",
    "Redotpay", "Tether TRC20", "Cwallet", "Tether BEP20", "Bybit", "MEXC"
])

sens = st.radio("Sens de conversion :", ["🔁 Ariary ➜ USD", "🔁 USD ➜ Ariary"])

# Entrée utilisateur
montant_ariary = 0
montant_usd = 0

if sens == "🔁 Ariary ➜ USD":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
else:
    montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=0.01)

# Taux & frais
if operation.startswith("Dépôt"):
    taux = 4750
    frais = 0.0
    if service in ["Skrill", "Neteller", "Payeer"]:
        if sens == "🔁 Ariary ➜ USD" and montant_ariary / taux <= 35:
            frais = 0.58
        else:
            frais = (montant_ariary * 0.0145 / taux) if sens == "🔁 Ariary ➜ USD" else (montant_usd * 0.0145)
    elif service == "Tether TRC20":
        frais = 1.00
else:
    taux = 4300 if service in ["Skrill", "Neteller", "Payeer", "AIRTM"] else 4400
    frais = 0.0  # Aucun frais sur retrait

# Calculs
if sens == "🔁 Ariary ➜ USD":
    montant_usd_brut = montant_ariary / taux
    montant_final = montant_usd_brut - frais
else:
    montant_ariary = (montant_usd + frais) * taux
    montant_final = montant_usd

# Affichage du résultat
st.markdown("### 💡 Résultat")
st.write(f"📤 Montant à envoyer : **{montant_final:.2f} USD**")
st.write(f"🔸 Frais appliqués : **{frais:.2f} USD**")
if sens == "🔁 USD ➜ Ariary":
    st.write(f"💵 Montant à recevoir : **{montant_ariary:.0f} Ar**")

# Historique
now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.session_state.historique.append({
    "Date": now,
    "Opération": operation,
    "Service": service,
    "Montant MGA": f"{montant_ariary:.0f} Ar",
    "Montant USD": f"{montant_final:.2f} USD",
    "Frais": f"{frais:.2f} USD"
})

# Copier ou exporter
if st.button("📋 Copier le résultat"):
    st.code(f"{montant_final:.2f} USD | {montant_ariary:.0f} Ar", language='text')

df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter CSV", data=df.to_csv().encode(), file_name="historique_261_exchange.csv", mime="text/csv")

# Affichage historique
if st.checkbox("📜 Voir l'historique de session"):
    st.dataframe(df)
