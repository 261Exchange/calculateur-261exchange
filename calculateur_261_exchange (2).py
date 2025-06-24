import streamlit as st

st.set_page_config(page_title="261 Exchange - Calculateur Pro", layout="centered")

st.title("📱 261 Exchange – Calculateur Pro") st.markdown(""" Calcule rapidement le solde à envoyer ou à recevoir selon le service, le taux et le sens d'opération. """)

Tarifs personnalisés

rates = { "Skrill": {"achat": 4750, "vente": 4300}, "Neteller": {"achat": 4750, "vente": 4300}, "Payeer": {"achat": 4750, "vente": 4300}, "AIRTM": {"achat": 4750, "vente": 4300}, "Binance": {"achat": 4750, "vente": 4400}, "OKX": {"achat": 4750, "vente": 4400}, "FaucetPay": {"achat": 4750, "vente": 4400}, "Bitget": {"achat": 4750, "vente": 4400}, "Redotpay": {"achat": 4750, "vente": 4400}, "Tether TRC20": {"achat": 4750, "vente": 4400}, "Cwallet": {"achat": 4750, "vente": 4400}, "Tether BEP20": {"achat": 4750, "vente": 4400}, "Bybit": {"achat": 4750, "vente": 4400}, "MEXC": {"achat": 4750, "vente": 4400}, "Deriv": {"achat": 4750, "vente": 4400}, }

operation_type = st.selectbox("Type d'opération", ["Dépôt (Ariary vers USD)", "Retrait (USD vers Ariary)"]) service = st.selectbox("Service utilisé", list(rates.keys()))

if operation_type == "Dépôt (Ariary vers USD)": ar_amount = st.number_input("Montant payé par le client (en Ariary)", min_value=0.0, step=100.0) taux = rates[service]["achat"] usd_equiv = ar_amount / taux st.success(f"💵 Montant à envoyer : {usd_equiv:.2f} USD") else: usd_amount = st.number_input("Montant à retirer (en USD)", min_value=0.0, step=1.0) taux = rates[service]["vente"] ar_equiv = usd_amount * taux st.success(f"💴 Montant à payer par le client : {ar_equiv:,.0f} MGA")

st.caption("Taux appliqué automatiquement selon le service. Mise à jour: Juin 2025.")
