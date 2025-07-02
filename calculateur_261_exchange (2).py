import streamlit as st
import requests
import datetime
import pandas as pd

# Config de la page
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")

st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calculez le montant en crypto ou en Ariary selon le sens de l’opération.")

# Liste des cryptos et frais
cryptos = {
    "tron": {"symbol": "TRX", "fee": 1},
    "bitcoin": {"symbol": "BTC", "fee": 0.00003},
    "ethereum": {"symbol": "ETH", "fee": 0.0004},
    "binancecoin": {"symbol": "BNB", "fee": 0.00009},
    "ripple": {"symbol": "XRP", "fee": 0.2},
    "dogecoin": {"symbol": "DOGE", "fee": 1},
    "solana": {"symbol": "SOL", "fee": 0.001},
    "litecoin": {"symbol": "LTC", "fee": 0.00015},
    "sui": {"symbol": "SUI", "fee": 0.07},
    "the-open-network": {"symbol": "TON", "fee": 0.03},
    "matic-network": {"symbol": "MATIC", "fee": 1},
    "core": {"symbol": "CORE", "fee": 1},
    "love-earned-enjoy": {"symbol": "LEE", "fee": 1}
}

# Fonction pour récupérer les prix sur CoinGecko
@st.cache_data(ttl=300)
def get_prices():
    ids = ",".join(cryptos.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.RequestException:
        return {}

# Appel API une seule fois
prices = get_prices()

if not prices:
    st.error("⚠️ Impossible de récupérer les prix CoinGecko. Trop de requêtes ou problème réseau. Réessayez plus tard.")
else:
    st.subheader("🔍 Prix unitaire d’une cryptomonnaie")
    selected_crypto = st.selectbox(
        "Choisir une crypto :",
        list(cryptos.keys()),
        format_func=lambda x: cryptos[x]["symbol"]
    )

    if selected_crypto in prices:
        st.info(f"💲 1 {cryptos[selected_crypto]['symbol']} = {prices[selected_crypto]['usd']} USD")

    # Définition des taux
    taux_crypto_depot = 4900
    taux_crypto_retrait = 4250
    taux_fiat = 4750
    taux_fiat_retrait = 4300
    taux_autres_retrait = 4400

    st.subheader("🔁 Conversion")
    operation = st.radio("Type d'opération :", ["Dépôt", "Retrait"])
    service = st.selectbox(
        "Service utilisé :",
        [
            "Skrill", "Neteller", "Payeer", "AIRTM",
            "Tether TRC20", "Tether BEP20"
        ] + list(cryptos.keys()) + ["Autre"]
    )
    sens = st.radio("Sens de conversion :", ["Ariary ➜ USD/Crypto", "USD/Crypto ➜ Ariary"])

    # Détermination du type et des paramètres
    is_crypto = service in cryptos
    frais = 0.0
    cours = prices.get(service, {}).get("usd") if is_crypto else None

    if is_crypto:
        taux = taux_crypto_depot if operation == "Dépôt" else taux_crypto_retrait
        frais = cryptos[service]['fee'] if operation == "Dépôt" else 0.0
    elif service == "Tether TRC20":
        taux = taux_fiat if operation == "Dépôt" else taux_autres_retrait
        frais = 1.0 if operation == "Dépôt" else 0.0
    elif service == "Tether BEP20":
        taux = taux_fiat if operation == "Dépôt" else taux_autres_retrait
        frais = 0.0
    elif service in ["Skrill", "Neteller", "Payeer", "AIRTM"]:
        taux = taux_fiat if operation == "Dépôt" else taux_fiat_retrait
    else:
        taux = taux_fiat if operation == "Dépôt" else taux_autres_retrait

    symbol = cryptos[service]['symbol'] if is_crypto else service

    if is_crypto and (cours is None or cours == 0):
        st.error(f"Impossible de récupérer le cours pour {service}. Veuillez réessayer plus tard.")
        st.stop()

    st.write("---")
    result_text = ""

    if sens == "Ariary ➜ USD/Crypto":
        montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
        montant_usd = montant_ariary / taux

        # Frais spéciaux Skrill / Neteller
        if service in ["Skrill", "Neteller"] and operation == "Dépôt":
            frais = 0.58 if montant_usd <= 35 else round(montant_usd * 0.0145, 2)

        if is_crypto or service.startswith("Tether"):
            montant_crypto = montant_usd / cours if cours else 0.0
            montant_final = montant_crypto - frais
            if montant_final < 0:
                montant_final = 0.0
            st.success(f"🪙 Montant à envoyer : {montant_final:.6f} {symbol}")
            st.write(f"💸 Frais appliqués : {frais} {symbol}")
            result_text = f"{montant_final:.6f} {symbol} | {montant_ariary:.0f} Ar"
        else:
            montant_final = montant_usd - frais
            if montant_final < 0:
                montant_final = 0.0
            st.success(f"💵 Montant à envoyer : {montant_final:.2f} USD")
            st.write(f"💸 Frais appliqués : {frais:.2f} USD")
            result_text = f"{montant_final:.2f} USD | {montant_ariary:.0f} Ar"

    else:
        if is_crypto or service.startswith("Tether"):
            montant_crypto = st.number_input(f"Montant à envoyer ({symbol})", min_value=0.0)
            montant_usd = montant_crypto * cours if cours else 0.0
            montant_ariary = montant_usd * taux
            st.success(f"💵 Montant à recevoir : {montant_ariary:.0f} Ar")
            st.write(f"💸 Frais appliqués : 0")
            result_text = f"{montant_crypto:.6f} {symbol} ➜ {montant_ariary:.0f} Ar"
        else:
            montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0)
            if service in ["Skrill", "Neteller"] and operation == "Dépôt":
                frais = 0.58 if montant_usd <= 35 else round(montant_usd * 0.0145, 2)
            montant_ariary = (montant_usd + frais) * taux
            st.success(f"💵 Montant à recevoir : {montant_ariary:.0f} Ar")
            st.write(f"💸 Frais appliqués : {frais:.2f} USD")
            result_text = f"{montant_usd:.2f} USD ➜ {montant_ariary:.0f} Ar"

    if result_text:
        st.markdown("### 📋 Copier le résultat")
        st.code(result_text)

    # Gestion historique
    if "historique" not in st.session_state:
        st.session_state.historique = []

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.historique.append({
        "Date": now,
        "Opération": operation,
        "Service": service,
        "Résultat": result_text,
        "Frais": f"{frais:.6f} {symbol}"
    })

    df = pd.DataFrame(st.session_state.historique)
    st.download_button(
        "⬇️ Exporter l'historique (CSV)",
        data=df.to_csv(index=False).encode(),
        file_name="historique_exchange.csv",
        mime="text/csv"
    )

    with st.expander("📜 Voir l'historique complet"):
        if df.empty:
            st.info("Aucune donnée dans l’historique pour le moment.")
        else:
            st.dataframe(df, use_container_width=True)

    # Affichage des taux des cryptos
    st.subheader("📊 Taux des devises")
    data_taux = []
    for key, info in cryptos.items():
        if key in prices:
            usd_price = prices[key]["usd"]
            ar_price = round(usd_price * taux_crypto_retrait)
            data_taux.append({
                "Crypto": info["symbol"],
                "Prix (USD)": usd_price,
                "Prix (Ar)": ar_price
            })

    df_taux = pd.DataFrame(data_taux)

    if df_taux.empty:
        st.warning("Aucun taux n’a pu être récupéré pour les cryptos.")
    else:
        st.dataframe(
            df_taux.style.background_gradient(cmap="Blues"),
            use_container_width=True
        )
