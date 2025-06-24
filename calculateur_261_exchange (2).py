import streamlit as st import datetime import io import pandas as pd

st.set_page_config(page_title="261 Exchange - Calculateur Pro", layout="centered")

st.image("https://i.imgur.com/O8Y6UeD.png", width=180)

st.title("Calculateur de conversion")

Taux personnalisés

Taux_DEPOT = 4750 Taux_RETRAIT_STANDARD = 4400 Taux_RETRAIT_SPECIAL = 4300 SERVICES_SPECIAUX = ["Skrill - USD", "Neteller - USD", "Payeer - USD", "AIRTM - USDC"] SERVICES = [ "Skrill - USD", "Neteller - USD", "Payeer - USD", "AIRTM - USDC", "Binance - USDT", "OKX - USDT", "FaucetPay - USDT", "Bitget - USDT", "Redotpay - USDT", "Tether TRC20 - USDT", "Cwallet - USDT", "Tether BEP20 - USDT", "Bybit - USDT", "MEXC - USDT", "Deriv - USD" ]

operation = st.radio("Type d'opération", ["Dépôt (Ariary → USD)", "Retrait (USD → Ariary)"]) service = st.selectbox("Service utilisé", SERVICES) mode = st.radio("Saisie de base", ["Montant en Ariary", "Montant en USD"])

result = {}

if operation == "Dépôt (Ariary → USD)": taux = Taux_DEPOT if mode == "Montant en Ariary": montant_ariary = st.number_input("Montant payé (Ar)", min_value=0.0, step=100.0) montant_usd = montant_ariary / taux else: montant_usd = st.number_input("Montant à envoyer (USD)", min_value=0.0, step=1.0) montant_ariary = montant_usd * taux

frais = 0.0
if service == "Tether TRC20 - USDT":
    frais = 1.0
elif service in ["Skrill - USD", "Neteller - USD"]:
    frais = 0.58 if montant_usd <= 35 else montant_usd * 0.0145

montant_usd_final = montant_usd - frais

result = {
    "Type": "Dépôt",
    "Service": service,
    "Montant payé (Ar)": montant_ariary,
    "Montant à envoyer (USD)": round(montant_usd_final, 2),
    "Frais": round(frais, 2),
    "Taux appliqué": taux
}

else: taux = Taux_RETRAIT_SPECIAL if service in SERVICES_SPECIAUX else Taux_RETRAIT_STANDARD if mode == "Montant en USD": montant_usd = st.number_input("Montant à retirer (USD)", min_value=0.0, step=1.0) montant_ariary = montant_usd * taux else: montant_ariary = st.number_input("Montant à recevoir (Ar)", min_value=0.0, step=100.0) montant_usd = montant_ariary / taux

result = {
    "Type": "Retrait",
    "Service": service,
    "Montant reçu (USD)": round(montant_usd, 2),
    "Montant à demander (Ar)": round(montant_ariary, 0),
    "Frais": 0.0,
    "Taux appliqué": taux
}

if result: st.subheader("Résultat") for k, v in result.items(): st.write(f"{k} : {v}")

col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Copier les résultats"):
        st.write("Résultats copiés !")
with col2:
    if st.button("🔄 Réinitialiser"):
        st.experimental_rerun()

export_format = st.selectbox("Exporter en format", ["CSV", "PDF (à venir)", "PNG (à venir)", "JPEG (à venir)"])
if export_format == "CSV":
    df = pd.DataFrame([result])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger CSV", csv, "resultat_261exchange.csv", "text/csv")

# Enregistrement de l'historique local
if "historique" not in st.session_state:
    st.session_state.historique = []
if st.button("🕘 Enregistrer dans l'historique"):
    st.session_state.historique.append({"datetime": str(datetime.datetime.now()), **result})

if st.checkbox("📂 Afficher l'historique"):
    histo_df = pd.DataFrame(st.session_state.historique)
    st.dataframe(histo_df)

st.caption("Version améliorée – 261 Exchange © 2025")

