import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Titolo
st.title("Simulatore Finanze Personali a Lungo Termine 🏡💰")

# --- INPUT ---
st.header("Parametri iniziali")
col1, col2 = st.columns(2)

with col1:
    liquidita_iniziale = st.number_input("Liquidità iniziale (€)", value=100000)
    risparmi_iniziali = st.number_input("Risparmi iniziali (investimento) (€)", value=0)
    stipendio = st.number_input("Stipendio netto mensile (€)", value=1700)
    spese_mensili = st.number_input("Spese fisse mensili (€)", value=800)
    spese_annuali = st.number_input("Spese fisse annuali (€)", value=1200)

with col2:
    risparmio_mensile = st.number_input("Risparmio mensile desiderato (€ o % dello stipendio)", value=200)
    come_percentuale = st.checkbox("Risparmio come % dello stipendio")
    anni = st.slider("Orizzonte temporale (anni)", 5, 40, 30)
    inflazione = st.slider("Inflazione media annua (%)", 0.0, 5.0, 2.0)

# Investimento
st.header("Profilo investimento")
profilo = st.selectbox("Profilo di rischio", ["Conservativo", "Bilanciato", "Aggressivo"])

rendimenti = {
    "Conservativo": (0.03, 0.04),
    "Bilanciato": (0.05, 0.07),
    "Aggressivo": (0.07, 0.10)
}

r_min, r_max = rendimenti[profilo]
rendimento_atteso = st.slider("Rendimento medio annuo investimento (%)", r_min * 100, r_max * 100,
                              (r_min + r_max) / 2 * 100) / 100

# Mutuo
st.header("Mutuo")
col3, col4 = st.columns(2)
with col3:
    importo_mutuo = st.number_input("Importo del mutuo (€)", value=200000)
    durata_mutuo = st.slider("Durata mutuo (anni)", 5, 35, 25)
with col4:
    tasso_interesse = st.slider("Tasso d'interesse mutuo (%)", 0.5, 6.0, 2.5)

# Detrazioni fiscali
st.header("Detrazioni Fiscali (seleziona applicabili)")
detrazioni = st.multiselect(
    "Seleziona le detrazioni applicabili",
    ["Mutuo prima casa", "Detrazione per ristrutturazione", "Altre spese deducibili"],
    default=["Mutuo prima casa"]
)

# --- CALCOLI ---
st.header("Simulazione")

# Funzione per calcolare il mutuo
mesi = anni * 12

r = tasso_interesse / 100 / 12  # tasso mensile
n = durata_mutuo * 12  # numero di rate mensili
P = importo_mutuo  # importo del mutuo
rata_mutuo = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


# Funzione per calcolare il flusso di cassa
def simula_scenario(stipendio, spese_mensili, spese_annuali, risparmio_mensile, come_percentuale, anni, inflazione,
                    rendimento_atteso, detrazioni):
    # Inizializzazione
    cc = liquidita_iniziale  # conto corrente
    investimento = risparmi_iniziali
    storico = []

    for mese in range(1, mesi + 1):
        anno_corrente = mese // 12
        risparmio_eff = (stipendio * risparmio_mensile / 100) if come_percentuale else risparmio_mensile

        # Inflazione sulle spese
        inflazione_factor = (1 + inflazione / 100) ** anno_corrente
        spese_m = spese_mensili * inflazione_factor
        spese_a = (spese_annuali / 12) * inflazione_factor

        spese_totali = spese_m + spese_a + (rata_mutuo if mese <= durata_mutuo * 12 else 0)

        # Applicazione delle detrazioni fiscali
        if "Mutuo prima casa" in detrazioni:
            detrazione_mutuo = importo_mutuo * 0.19 / 12  # esempio: 19% su importo
        else:
            detrazione_mutuo = 0

        spese_totali -= detrazione_mutuo  # applica la detrazione

        # Cash flow
        utile = stipendio - spese_totali
        in_investimento = risparmio_eff
        in_cc = utile - risparmio_eff

        if in_cc < 0:
            in_investimento += in_cc  # togliamo dai risparmi per pareggiare
            in_cc = 0

        cc += in_cc
        investimento *= (1 + rendimento_atteso / 12)  # rendimento mensile
        investimento += max(0, in_investimento)

        storico.append([mese / 12, cc, investimento, cc + investimento])

    return pd.DataFrame(storico, columns=["Anno", "Conto Corrente", "Investimento", "Totale"])


# Scenario 1
df1 = simula_scenario(stipendio, spese_mensili, spese_annuali, risparmio_mensile, come_percentuale, anni, inflazione,
                      rendimento_atteso, detrazioni)

# Scenario 2 (con altre variabili, esempio tasso interesse diverso)
tasso_interesse2 = st.slider("Tasso d'interesse scenario 2 (%)", 0.5, 6.0, 3.0)
df2 = simula_scenario(stipendio, spese_mensili, spese_annuali, risparmio_mensile, come_percentuale, anni, inflazione,
                      rendimento_atteso, detrazioni)

# --- OUTPUT ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df1["Anno"], df1["Conto Corrente"], label="Conto Corrente Scenario 1")
ax.plot(df1["Anno"], df1["Investimento"], label="Investimento Scenario 1")
ax.plot(df1["Anno"], df1["Totale"], label="Totale Patrimonio Scenario 1", linestyle="--")
ax.plot(df2["Anno"], df2["Conto Corrente"], label="Conto Corrente Scenario 2")
ax.plot(df2["Anno"], df2["Investimento"], label="Investimento Scenario 2")
ax.plot(df2["Anno"], df2["Totale"], label="Totale Patrimonio Scenario 2", linestyle="--")
ax.set_ylabel("€")
ax.set_xlabel("Anno")
ax.set_title("Confronto tra due scenari")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# Mostra tabella opzionale
if st.checkbox("Mostra dati tabellari"):
    st.dataframe(df1.round(2))
    st.dataframe(df2.round(2))
