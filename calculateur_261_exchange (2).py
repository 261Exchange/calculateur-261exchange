
import streamlit as st

st.set_page_config(page_title="261 Exchange – Calculateur Pro", page_icon="💱")

st.title("📱 261 Exchange – Calculateur Pro")
st.write("Calcule rapidement le solde à envoyer à tes clients selon le taux, les frais, et le service choisi.")

operation = st.selectbox("Type d'opération :", ["Dépôt (4750 Ar/USD)", "Retrait Skrill/Neteller (4300 Ar/USD)", "Autres Retraits (4400 Ar/USD)"])
service = st.selectbox("Service utilisé :", ["Deriv", "Binance", "USDT TRC20", "Skrill", "Neteller"])
montant_ariary = st.number_input("Montant payé par le client (en Ariary)", min_value=0.0, step=1000.0)
marge = st.number_input("Marge appliquée (%)", min_value=0.0, step=0.5)

# Déterminer le taux selon l'opération
if operation == "Dépôt (4750 Ar/USD)":
    taux = 4750
elif operation == "Retrait Skrill/Neteller (4300 Ar/USD)":
    taux = 4300
else:
    taux = 4400

# Conversion brut (sans marge)
montant_usd_brut = montant_ariary / taux
montant_usd_net = montant_usd_brut * (1 - marge / 100)

# Application des frais selon le service
frais = 0.0
if service == "USDT TRC20":
    frais = 1.0
elif service in ["Skrill", "Neteller"]:
    if montant_usd_net > 35:
        frais = montant_usd_net * 0.0145
    else:
        frais = 0.58

# Résultat final
montant_final = montant_usd_net - frais
benefice = montant_usd_brut - montant_usd_net

st.markdown("### 💡 Résultat")
st.write(f"🔹 **Montant à envoyer** : {montant_final:.2f} USD")
st.write(f"🔸 **Frais appliqués** : {frais:.2f} USD")
st.write(f"🟢 **Bénéfice net estimé** : {benefice:.2f} USD")
