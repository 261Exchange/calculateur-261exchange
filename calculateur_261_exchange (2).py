import streamlit as st
import datetime
import pandas as pd
from PIL import Image, ImageDraw
import io

# Configuration de la page
st.set_page_config(page_title="261 Exchange – Calculateur Pro", layout="centered")

# Logo
st.image("https://261exchange.com/logo.png", width=200)

st.title("💱 261 Exchange – Calculateur Pro")
st.write("Calcule rapidement le montant à envoyer ou à recevoir selon le taux, les frais et le sens de conversion.")

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

# Fonction de calcul des frais
def calcul_frais(service, sens, montant_ariary, montant_usd, taux):
    if service in ["Skrill", "Neteller", "Payeer"]:
        if sens == "🔁 Ariary ➔ USD" and montant_ariary / taux <= 35:
            return 0.58
        else:
            return (montant_ariary * 0.0145 / taux) if sens == "🔁 Ariary ➔ USD" else (montant_usd * 0.0145)
    elif service == "Tether TRC20":
        return 1.00
    return 0.0

# Fonction pour créer une image du résultat
def create_result_image(montant_usd, montant_ariary, frais):
    img = Image.new("RGB", (600, 200), color="white")
    d = ImageDraw.Draw(img)
    d.text((10, 20), f"Montant à envoyer : {montant_usd:.2f} USD", fill="black")
    d.text((10, 60), f"Frais appliqués : {frais:.2f} USD", fill="black")
    d.text((10, 100), f"Montant à recevoir : {montant_ariary:.0f} Ar", fill="black")
    return img

# Formulaire
operation = st.selectbox("Type d'opération :", ["Dépôt (4750 Ar/USD)", "Retrait (4400 Ar/USD sauf 4300 Ar)"])
service = st.selectbox("Service utilisé :", [
    "Deriv", "Skrill", "Neteller", "Payeer", "AIRTM", "Binance", "OKX", "FaucetPay", "Bitget",
    "Redotpay", "Tether TRC20", "Cwallet", "Tether BEP20", "Bybit", "MEXC"
])

sens = st.radio("Sens de conversion :", ["🔁 Ariary ➔ USD", "🔁 USD ➔ Ariary"])

# Entrées utilisateur
montant_ariary = 0.0
montant_usd = 0.0

if sens == "🔁 Ariary ➔ USD":
    montant_ariary = st.number_input("Montant payé (en Ariary)", min_value=0.0, step=1000.0)
else:
    montant_usd = st.number_input("Montant à envoyer (en USD)", min_value=0.0, step=0.01)

# Taux et frais
if operation.startswith("Dépôt"):
    taux = 4750
else:
    taux = 4300 if service in ["Skrill", "Neteller", "Payeer", "AIRTM"] else 4400

frais = calcul_frais(service, sens, montant_ariary, montant_usd, taux)

# Calculs et affichage
if (sens == "🔁 Ariary ➔ USD" and montant_ariary > 0) or (sens == "🔁 USD ➔ Ariary" and montant_usd > 0):
    if sens == "🔁 Ariary ➔ USD":
        montant_usd_brut = montant_ariary / taux
        montant_final = montant_usd_brut - frais
    else:
        montant_ariary = round((montant_usd + frais) * taux, -1)  # arrondi aux 10 Ar
        montant_final = montant_usd

    st.markdown("### 💡 Résultat")
    st.write(f"📤 Montant à envoyer : **{montant_final:.2f} USD**")
    st.write(f"🔸 Frais appliqués : **{frais:.2f} USD**")
    if sens == "🔁 USD ➔ Ariary":
        st.write(f"💵 Montant à recevoir : **{montant_ariary:.0f} Ar**")

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.historique.append({
        "Date": now,
        "Opération": operation,
        "Service": service,
        "Montant MGA": f"{montant_ariary:.0f} Ar",
        "Montant USD": f"{montant_final:.2f} USD",
        "Frais": f"{frais:.2f} USD"
    })

    if st.button("📋 Copier le résultat"):
        st.code(f"{montant_final:.2f} USD | {montant_ariary:.0f} Ar", language='text')

    if st.button("📷 Exporter en PNG"):
        img = create_result_image(montant_final, montant_ariary, frais)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("Télécharger l'image", buf.getvalue(), "resultat.png", mime="image/png")

# Export & Historique
if st.button("🔄 Réinitialiser l'historique"):
    st.session_state.historique = []

if st.session_state.historique:
    df = pd.DataFrame(st.session_state.historique)
    st.download_button("⬇️ Exporter CSV", data=df.to_csv().encode(), file_name="historique_261_exchange.csv", mime="text/csv")

    if st.checkbox("📜 Voir l'historique de session"):
        st.dataframe(df)
