import streamlit as st
import datetime
import pandas as pd
import requests
import matplotlib.pyplot as plt
from io import BytesIO

# Configuration de la page
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")

# Logo
st.image("https://261exchange.com/logo.png", width=200)

st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calcule rapidement le montant à envoyer ou à recevoir selon le taux, les frais et le sens de conversion.")

# Récupération des cours crypto
crypto_ids = {
    "TRX": "tron",
    "BNB": "binancecoin",
    "ETH": "ethereum",
    "BTC": "bitcoin",
    "XRP": "ripple",
    "SOL": "solana",
    "DOGE": "dogecoin",
    "LTC": "litecoin",
    "SUI": "sui",
    "MATIC": "polygon",
    "TON": "the-open-network"
}

crypto_frais = {
    "TRX": 1,
    "BNB": 0.00009,
    "ETH": 0.0004,
    "BTC": 0.00003,
    "XRP": 0.2,
    "SOL": 0.001,
    "DOGE": 1,
    "LTC": 0.00015,
    "SUI": 0.07,
    "MATIC": 1,
    "TON": 0.03
}

url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(crypto_ids.values())}&vs_currencies=usd"
response = requests.get(url)
crypto_prices = response.json()

# Affichage des taux
st.subheader("📊 Cours actuels des cryptomonnaies")
for symbol, coingecko_id in crypto_ids.items():
    usd_price = crypto_prices[coingecko_id]["usd"]
    ar_depot = usd_price * 4850
    ar_retrait = usd_price * 4300
    st.markdown(f"**{symbol}**: {usd_price:.6f} USD | Dépôt: {ar_depot:,.0f} Ar | Retrait: {ar_retrait:,.0f} Ar")

# Historique utilisateur
if "historique" not in st.session_state:
    st.session_state.historique = []

# Formulaire utilisateur
operation = st.selectbox("Type d'opération :", ["Dépôt (4850 Ar/USD)", "Retrait (4300 Ar/USD sauf 4400 Ar)"])
service = st.selectbox("Service utilisé :", [
    "Deriv", "Skrill", "Neteller", "Payeer", "AIRTM", "Binance", "OKX", "FaucetPay", "Bitget",
    "Redotpay", "Tether TRC20", "Cwallet", "Tether BEP20", "Bybit", "MEXC",
    "TRX", "BNB", "ETH", "BTC", "XRP", "SOL", "DOGE", "LTC", "SUI", "MATIC", "TON"
])

sens = st.radio("Sens de conversion :", ["🔁 Ariary ➜ USD", "🔁 USD ➜ Ariary"])

# Entrées utilisateur
montant_ariary = 0
montant_usd = 0

if sens == "🔁 Ariary ➜ USD":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
else:
    montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=0.01)

# Taux & frais
is_crypto = service in crypto_ids.keys()

if operation.startswith("Dépôt"):
    taux = 4850
    frais = 0.0
    if is_crypto:
        usd_price = crypto_prices[crypto_ids[service]]["usd"]
        frais = usd_price * crypto_frais[service]
    elif service in ["Skrill", "Neteller", "Payeer"]:
        if sens == "🔁 Ariary ➜ USD" and montant_ariary / taux <= 35:
            frais = 0.58
        else:
            frais = (montant_ariary * 0.0145 / taux) if sens == "🔁 Ariary ➜ USD" else (montant_usd * 0.0145)
    elif service == "Tether TRC20":
        frais = 1.00
else:
    taux = 4300 if (is_crypto or service in ["Skrill", "Neteller", "Payeer", "AIRTM"]) else 4400
    frais = 0.0

# Calcul
if sens == "🔁 Ariary ➜ USD":
    montant_usd_brut = montant_ariary / taux
    montant_final = montant_usd_brut - frais
else:
    montant_ariary = (montant_usd + frais) * taux
    montant_final = montant_usd

# Résultat utilisateur
st.markdown("### 💡 Résultat")
st.write(f"📤 Montant à envoyer : **{montant_final:.2f} USD**")
st.write(f"🔸 Frais appliqués : **{frais:.6f} USD**")
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
    "Frais": f"{frais:.6f} USD"
})

# Copier et exporter
if st.button("📋 Copier le résultat"):
    st.code(f"{montant_final:.2f} USD | {montant_ariary:.0f} Ar", language='text')

df = pd.DataFrame(st.session_state.historique)
st.download_button("⬇️ Exporter CSV", data=df.to_csv().encode(), file_name="historique_261_exchange.csv", mime="text/csv")

# Export PNG
if st.button("🖼️ Exporter en PNG"):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')
    detail = [
        ["Date", now],
        ["Opération", operation],
        ["Service", service],
        ["Sens", sens],
        ["Taux utilisé", f"{taux:.0f} Ar/USD"],
        ["Frais", f"{frais:.6f} USD"],
        ["Montant payé (MGA)", f"{montant_ariary:.0f} Ar" if montant_ariary > 0 else "-"],
        ["Montant à envoyer (USD)", f"{montant_usd:.2f} USD" if montant_usd > 0 else "-"],
        ["Montant final reçu", f"{montant_final:.2f} USD" if sens == "🔁 Ariary ➜ USD" else f"{montant_ariary:.0f} Ar"]
    ]
    table = ax.table(cellText=detail, colLabels=["Détail", "Valeur"], loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    st.download_button("📥 Télécharger le PNG", data=buf.getvalue(), file_name="calcul_261_exchange.png", mime="image/png")

# Accès admin
st.markdown("---")
admin_pw = st.text_input("🔒 Mot de passe admin", type="password")
if admin_pw == "admin261exchange":
    st.success("✅ Accès administrateur autorisé")
    st.subheader("📜 Historique complet de session")
    st.dataframe(df)
else:
    st.info("Seul l’administrateur peut consulter l’historique complet.")
