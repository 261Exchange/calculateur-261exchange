import streamlit as st import datetime import pandas as pd import requests import matplotlib.pyplot as plt from io import BytesIO import base64

Configuration de la page

st.set_page_config(page_title="261 Exchange – Calculateur Pro") st.image("https://raw.githubusercontent.com/261Exchange/calculateur-261exchange/main/logo_261exchange.png", width=200)

st.title("261 Exchange – Calculateur Pro") st.write("Calcule rapidement le solde à envoyer à tes clients selon le taux, les frais, et le service choisi.")

Définition des cryptomonnaies avec frais (uniquement pour les dépôts)

crypto_fees = { "TRX": 1, "BNB": 0.00009, "ETH": 0.0004, "BTC": 0.00003, "XRP": 0.2, "SOL": 0.001, "DOGE": 1, "LTC": 0.00015, "SUI": 0.07, "MATIC": 1, "TON": 0.03 }

Saisie des données

operation = st.selectbox("Type d'opération :", ["Dépôt (4850 Ar/USD)", "Retrait (4300 Ar/USD)"]) service = st.selectbox("Crypto utilisée :", list(crypto_fees.keys()))

col1, col2 = st.columns(2) with col1: montant_ariary = st.number_input("Montant payé en Ariary", min_value=0.0, value=0.0, step=1000.0) with col2: montant_usd = st.number_input("Montant en USD", min_value=0.0, value=0.0, step=1.0)

Calcul automatique selon la saisie

if montant_usd > 0: taux = 4850 if operation == "Dépôt (4850 Ar/USD)" else 4300 montant_ariary = montant_usd * taux elif montant_ariary > 0: taux = 4850 if operation == "Dépôt (4850 Ar/USD)" else 4300 montant_usd = montant_ariary / taux

Application des frais uniquement sur les dépôts

frais_crypto = crypto_fees[service] if operation == "Dépôt (4850 Ar/USD)" else 0

Affichage du résultat

st.markdown("""

💡 Résultat

🔹 Montant à envoyer : {:.2f} {}

🟠 Frais appliqués : {:.6f} {}

📅 Détail : {} Ar / USD x {:.2f} USD = {:.2f} Ar """.format(montant_usd, service, frais_crypto, service, taux, montant_usd, montant_ariary))


Export PNG

if st.button("📂 Exporter en PNG"): fig, ax = plt.subplots() ax.axis('off') ax.text(0.01, 0.9, f"261 Exchange – Calculateur Pro", fontsize=14, fontweight='bold') ax.text(0.01, 0.7, f"Montant à envoyer : {montant_usd:.2f} {service}") ax.text(0.01, 0.6, f"Frais appliqués : {frais_crypto:.6f} {service}") ax.text(0.01, 0.5, f"Taux utilisé : {taux} Ar/USD") ax.text(0.01, 0.4, f"Montant total en Ariary : {montant_ariary:.2f} Ar") buf = BytesIO() plt.savefig(buf, format="png") st.image(buf)

Copier / partager (affichage HTML simplifié)

resultat = f"Montant: {montant_usd:.2f} {service}\nFrais: {frais_crypto:.6f} {service}\nTotal en Ar: {montant_ariary:.2f} Ar" st.code(resultat)

Historique (simple sauvegarde dans session)

if 'historique' not in st.session_state: st.session_state['historique'] = []

if st.button("✅ Enregistrer l'historique"): st.session_state['historique'].append({ 'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 'operation': operation, 'crypto': service, 'usd': montant_usd, 'ariary': montant_ariary, 'frais': frais_crypto })

if st.checkbox("📃 Voir l'historique"): historique_df = pd.DataFrame(st.session_state['historique']) st.dataframe(historique_df)

