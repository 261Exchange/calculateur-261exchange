import streamlit as st import datetime import pandas as pd import requests from io import BytesIO

Configuration de la page et affichage du logo

st.set_page_config(page_title="261 Exchange – Calculateur Pro") st.image("https://raw.githubusercontent.com/261Exchange/calculateur-261exchange/main/logo_261exchange.png", width=200)

st.title("261 Exchange – Calculateur Pro") st.write("Calcule rapidement le solde à envoyer à tes clients selon le taux, les frais, et le service choisi.")

Données de frais de dépôt pour cryptomonnaies

crypto_frais = { "Tron": 1, "BNB": 0.00009, "ETH": 0.0004, "BTC": 0.00003, "XRP": 0.2, "SOL": 0.001, "Doge": 1, "LTC": 0.00015, "SUI": 0.07, "Polygone": 1, "Toncoin": 0.03 }

Liste des services

services = list(crypto_frais.keys()) + ["Skrill", "Neteller", "Payeer", "AIRTM", "Deriv"]

Interface utilisateur

operation = st.selectbox("Type d'opération :", ["Dépôt (4850 Ar/USD)", "Retrait (4300 Ar/USD sauf 4 autres à 4400 Ar)"]) service = st.selectbox("Service utilisé :", services)

mode_saisie = st.radio("Choisir le mode de calcul :", ["Montant payé en Ariary", "Montant à envoyer en USD"])

if mode_saisie == "Montant payé en Ariary": montant_ariary = st.number_input("Montant payé par le client (en Ariary)", min_value=0.0, step=100.0) else: montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=1.0)

Détermination du taux

if operation.startswith("Dépôt"): taux = 4850 frais = crypto_frais.get(service, 0) else: taux = 4300 if service in crypto_frais else 4400 frais = 0.0

Calcul

if mode_saisie == "Montant payé en Ariary" and montant_ariary: montant_usd = montant_ariary / taux montant_net = montant_usd - frais elif mode_saisie == "Montant à envoyer en USD" and montant_usd: montant_ariary = (montant_usd + frais) * taux montant_net = montant_usd else: montant_net = 0.0

Affichage des résultats

st.markdown("""

💡 Résultat

🔹 Montant à envoyer : %.2f USD

🟠 Frais appliqués : %.2f USD

📊 Montant payé par le client : %.0f Ariary

🔢 Détail du calcul : %.2f USD + %.2f USD de frais × %.0f Ar/USD """ % (montant_net, frais, montant_ariary if mode_saisie == "Montant payé en Ariary" else montant_ariary, montant_net, frais, taux))


Export PNG

from matplotlib import pyplot as plt fig, ax = plt.subplots() ax.axis('off') texte = f"Service : {service}\nType : {operation}\nMontant client : {montant_ariary:.0f} Ar\nMontant USD : {montant_net:.2f} USD\nFrais : {frais:.2f} USD" ax.text(0.5, 0.5, texte, fontsize=12, ha='center', va='center') buffer = BytesIO() fig.savefig(buffer, format="png") st.download_button("📁 Exporter en PNG", buffer.getvalue(), file_name="calcul.png", mime="image/png")

Copier et partager

if st.button("🔍 Copier le résultat"): st.code(texte, language='text')

