import streamlit as st 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
import math
import os
import sys


# %% Color palettes
blue = sns.mpl_palette("Blues", 48)
red = sns.mpl_palette("Reds", 48)
green = sns.mpl_palette("Greens", 48)

# %% Functions
# Overheating calculation function [for period --> lenght according to lenght of period]
def exceeding_hours_TM52(extTemp, temp, climatic_zone):
    # Calculate running mean temperature
    alpha = 0.8
    days = 7
    dailyMeans = extTemp.reshape(-1, 24).mean(axis=1)
    Trm = np.zeros_like(dailyMeans)
    for i in range(len(dailyMeans)):
        temps = dailyMeans[max(0, i-days):i][::-1]
        if len(temps) > 0:
            weighted = sum((1-alpha) * (alpha ** n) *
                           t for n, t in enumerate(temps))
            Trm[i] = (weighted / (1-alpha ** len(temps)))
        else:
            Trm[i] = (dailyMeans[i])

    Trm = np.repeat(Trm, 24)

    # Comfort bands
    Tmin1 = 0.33 * Trm + 18.8 - 3
    Tmax1 = 0.33 * Trm + 18.8 + 2
    Tmax1_vent = Tmax1 + 2

    Tmin2 = 0.33 * Trm + 18.8 - 4
    Tmax2 = 0.33 * Trm + 18.8 + 3
    Tmax2_vent = Tmax2 + 2

    Tmin3 = 0.33 * Trm + 18.8 - 5
    Tmax3 = 0.33 * Trm + 18.8 + 4
    Tmax3_vent = Tmax3 + 2

    # Calculate comfort temperature [Second category]
    Tmax = 0.33 * Trm + 18.8 + 3
    Tmax_vent = Tmax + 2  # Adding ventilation -> comfort band is extended

    # Criterion 1 - Exceeding hours during occupied hours
    date_index = pd.date_range(
        temp.index[0], periods=extTemp.shape[0], freq="h")
    df = pd.DataFrame({"DateTime": date_index, "IndoorTemp": temp, "Threshold": Tmax, "ThresholdVent": Tmax_vent, "Tmin1": Tmin1, "Tmax1": Tmax1,
                      "Tmax1Vent": Tmax1_vent, "Tmin2": Tmin2, "Tmax2": Tmax2, "Tmax2Vent": Tmax2_vent, "Tmin3": Tmin3, "Tmax3": Tmax3, "Tmax3Vent": Tmax3_vent})

    df["Month"] = df["DateTime"].dt.month
    df["Weekday"] = df["DateTime"].dt.weekday  # Monday=0, Sunday=6
    df["Hour"] = df["DateTime"].dt.hour
    df["Date"] = df["DateTime"].dt.date

    occupied_months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                       11, 12]        # May, June, July, September
    occupied_weekdays = [0, 1, 2, 3, 4]   # Monday to Friday
    occupied_hours = range(8, 18)

    df["Occupied"] = (df["Month"].isin(occupied_months) & df["Weekday"].isin(
        occupied_weekdays) & df["Hour"].isin(occupied_hours))

    df_summer = df

    df_summer["Exceeds"] = (df_summer["IndoorTemp"] > (
        df_summer["Threshold"]+1)) & df_summer["Occupied"]
    df_summer["ExceedsVent"] = (df_summer["IndoorTemp"] > (
        df_summer["ThresholdVent"]+1)) & df_summer["Occupied"]

    occupied_count = df_summer["Occupied"].sum()
    exceed_count = df_summer["Exceeds"].sum()
    exceedVent_count = df_summer["ExceedsVent"].sum()

    percentC1 = exceed_count / occupied_count * 100 if occupied_count > 0 else 0
    percentC1Vent = exceedVent_count / \
        occupied_count * 100 if occupied_count > 0 else 0

    # Criterion  2 - Degree hours exceedence
    df_occ = df_summer[df_summer["Occupied"]].copy()
    df_occ["C2"] = np.where(df_occ["IndoorTemp"] > df_occ["Threshold"],
                            df_occ["IndoorTemp"] - df_occ["Threshold"], 0)
    dailyDH = df_occ.groupby("DateTime")["C2"].sum()
    days_exceeded_C2 = (dailyDH > 6).sum()
    tot_days = len(dailyDH)

    percentC2 = days_exceeded_C2 / tot_days * 100 if tot_days > 0 else 0

    df_occ["C2Vent"] = np.where(df_occ["IndoorTemp"] > df_occ["ThresholdVent"],
                                df_occ["IndoorTemp"] - df_occ["ThresholdVent"], 0)
    dailyDHVent = df_occ.groupby("DateTime")["C2Vent"].sum()
    days_exceeded_C2Vent = (dailyDHVent > 6).sum()
    tot_daysVent = len(dailyDHVent)

    percentC2Vent = days_exceeded_C2Vent / \
        tot_daysVent * 100 if tot_daysVent > 0 else 0

    # Criterion 3 - Upper limit
    C3_exceed_hours = (
        (df_summer["IndoorTemp"] > df_summer["Threshold"] + 4) & df_summer["Occupied"]).sum()
    percentC3 = C3_exceed_hours / occupied_count * 100 if occupied_count > 0 else 0
    C3_exceed_hoursVent = (
        (df_summer["IndoorTemp"] > df_summer["ThresholdVent"] + 4) & df_summer["Occupied"]).sum()
    percentC3Vent = C3_exceed_hoursVent / \
        occupied_count * 100 if occupied_count > 0 else 0

    # Overheating assessment
    if (percentC1 > 3) & (percentC2 > 0):
        overheating = "True"
    elif (percentC1 > 3) & (percentC3 > 0):
        overheating = "True"
    elif (percentC2 > 0) & (percentC3 > 0):
        overheating = "True"
    else:
        overheating = "False"

    # Overheating assessment Vent
    if (percentC1Vent > 3) & (percentC2Vent > 0):
        overheatingVent = "True"
    elif (percentC1Vent > 3) & (percentC3Vent > 0):
        overheatingVent = "True"
    elif (percentC2Vent > 0) & (percentC3Vent > 0):
        overheatingVent = "True"
    else:
        overheatingVent = "False"

    # Dist from Tmax
    dist = df_occ["C2"]
    distVent = df_occ["C2Vent"]

    dist_df = pd.DataFrame({"without_vent": dist, "with_vent": distVent})

    # Comfort bands
    df_summer["low"] = (df_summer["IndoorTemp"] <
                        df_summer["Tmin3"]) & df_summer["Occupied"]
    df_summer["lowBand3"] = (df_summer["IndoorTemp"] > df_summer["Tmin3"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmin2"]) & df_summer["Occupied"]
    df_summer["lowBand2"] = (df_summer["IndoorTemp"] > df_summer["Tmin2"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmin1"]) & df_summer["Occupied"]
    df_summer["Band1"] = (df_summer["IndoorTemp"] > df_summer["Tmin1"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmax1"]) & df_summer["Occupied"]
    df_summer["highBand2"] = (df_summer["IndoorTemp"] > df_summer["Tmax1"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmax2"]) & df_summer["Occupied"]
    df_summer["highBand3"] = (df_summer["IndoorTemp"] > df_summer["Tmax2"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmax3"]) & df_summer["Occupied"]
    df_summer["high"] = (df_summer["IndoorTemp"] >
                         df_summer["Tmax3"]) & df_summer["Occupied"]

    df_summer["lowVent"] = (df_summer["IndoorTemp"] <
                            df_summer["Tmin3"]) & df_summer["Occupied"]
    df_summer["lowBand3Vent"] = (df_summer["IndoorTemp"] > df_summer["Tmin3"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmin2"]) & df_summer["Occupied"]
    df_summer["lowBand2Vent"] = (df_summer["IndoorTemp"] > df_summer["Tmin2"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmin1"]) & df_summer["Occupied"]
    df_summer["Band1Vent"] = (df_summer["IndoorTemp"] > df_summer["Tmin1"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmax1Vent"]) & df_summer["Occupied"]
    df_summer["highBand2Vent"] = (df_summer["IndoorTemp"] > df_summer["Tmax1Vent"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmax2Vent"]) & df_summer["Occupied"]
    df_summer["highBand3Vent"] = (df_summer["IndoorTemp"] > df_summer["Tmax2Vent"]) & (
        df_summer["IndoorTemp"] < df_summer["Tmax3Vent"]) & df_summer["Occupied"]
    df_summer["highVent"] = (df_summer["IndoorTemp"] >
                             df_summer["Tmax3Vent"]) & df_summer["Occupied"]

    low = df_summer["low"].sum() / occupied_count * \
        100 if occupied_count > 0 else 0
    lowBand3 = df_summer["lowBand3"].sum() / occupied_count * \
        100 if occupied_count > 0 else 0
    lowBand2 = df_summer["lowBand2"].sum() / occupied_count * \
        100 if occupied_count > 0 else 0
    Band1 = df_summer["Band1"].sum() / occupied_count * \
        100 if occupied_count > 0 else 0
    highBand2 = df_summer["highBand2"].sum(
    ) / occupied_count * 100 if occupied_count > 0 else 0
    highBand3 = df_summer["highBand3"].sum(
    ) / occupied_count * 100 if occupied_count > 0 else 0
    high = df_summer["high"].sum() / occupied_count * \
        100 if occupied_count > 0 else 0

    lowVent = df_summer["lowVent"].sum() / occupied_count * \
        100 if occupied_count > 0 else 0
    lowBand3Vent = df_summer["lowBand3Vent"].sum(
    ) / occupied_count * 100 if occupied_count > 0 else 0
    lowBand2Vent = df_summer["lowBand2Vent"].sum(
    ) / occupied_count * 100 if occupied_count > 0 else 0
    Band1Vent = df_summer["Band1Vent"].sum(
    ) / occupied_count * 100 if occupied_count > 0 else 0
    highBand2Vent = df_summer["highBand2Vent"].sum(
    ) / occupied_count * 100 if occupied_count > 0 else 0
    highBand3Vent = df_summer["highBand3Vent"].sum(
    ) / occupied_count * 100 if occupied_count > 0 else 0
    highVent = df_summer["highVent"].sum() / occupied_count * \
        100 if occupied_count > 0 else 0

    return (temp, Trm, Tmax, percentC1, percentC2, percentC3, overheating, Tmax_vent, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, dist_df, low, lowBand3, lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent)

# Climatic zone

def climzone(climatic_zone):
    if climatic_zone == "A":
        city = "LA"
        startNH = "2025-03-16 00:00:00"
        endNH = "2025-12-01 00:00:00"
        xgen = -0.3
        xfeb = 0
        xmar = 0.4
        xapr = 0.8
        xmay = 1.2
        xjun = 1.7
        xjul = 2
        xaug = 2.3
        xsep = 2.7
        xoct = 3
        xnov = 3.3
        xdec = 4
    elif climatic_zone == "B":
        city = "PA"
        startNH = "2025-04-01 00:00:00"
        endNH = "2025-12-01 00:00:00"
        xgen = -0.3
        xfeb = 0
        xmar = 0.3
        xapr = 0.8
        xmay = 1.2
        xjun = 1.7
        xjul = 2
        xaug = 2.3
        xsep = 2.7
        xoct = 3
        xnov = 3.3
        xdec = 4
    elif climatic_zone == "C":
        city = "NA"
        startNH = "2025-04-01 00:00:00"
        endNH = "2025-11-15 00:00:00"
        xgen = -0.3
        xfeb = 0
        xmar = 0.3
        xapr = 0.8
        xmay = 1.2
        xjun = 1.7
        xjul = 2
        xaug = 2.3
        xsep = 2.8
        xoct = 3.2
        xnov = 3.5
        xdec = 4
    elif climatic_zone == "D":
        city = "RO"
        startNH = "2025-04-16 00:00:00"
        endNH = "2025-11-01 00:00:00"
        xgen = -0.4
        xfeb = -0.15
        xmar = 0.15
        xapr = 0.5
        xmay = 1
        xjun = 1.7
        xjul = 2
        xaug = 2.3
        xsep = 2.8
        xoct = 3.2
        xnov = 3.8
        xdec = 4.2
    elif climatic_zone == "E":
        city = "MI"
        startNH = "2025-04-16 00:00:00"
        endNH = "2025-10-15 00:00:00"
        xgen = -0.4
        xfeb = -0.15
        xmar = 0.15
        xapr = 0.5
        xmay = 1
        xjun = 1.7
        xjul = 2
        xaug = 2.3
        xsep = 3
        xoct = 3.5
        xnov = 3.8
        xdec = 4.2
    elif climatic_zone == "F":
        city = "CU"
        startNH = "2025-04-16 00:00:00"
        endNH = "2025-10-15 00:00:00"  # Nessuna limitazione
        xgen = -0.4
        xfeb = -0.15
        xmar = 0.15
        xapr = 0.5
        xmay = 1
        xjun = 1.7
        xjul = 2
        xaug = 2.3
        xsep = 3
        xoct = 3.7
        xnov = 4
        xdec = 4.3
        
    return(city, startNH, endNH, xgen, xfeb, xmar, xapr, xmay, xjun, xjul, xaug, xsep, xoct, xnov, xdec)

#%% Inputs

st.title("Tool per l'identificazione della condizione di overheating nell'intero edificio scolastico")
st.write("Questo tool permette di analizzare il potenziale di overheating dell'intero edificio scolastico, sulla base della localizzazione e delle caratteristiche geometriche, di involucro e di ventilazione delle aule")

st.subheader("Dati riguardanti l'edificio scolastico", divider = True)
climatic_zone = st.radio("Selezionare la zona climatica", ["A", "B", "C", "D", "E", "F"], index = None, horizontal = True)
numeroAULE = st.number_input("Inserire il numero totale di aule della scuola:", min_value = 0)
number_of_types = st.slider("Selezionare il numero di gruppi di aule scolastiche aggregabili per piano, posizione e orientamento", 0, 10)
supVetrata = st.slider("Indicare il rapporto superficie vetrata / superficie del pavimento in %", 0, 100)   
g = st.slider("Indicare il fattore solare (g-value) dei vetri", 0.0, 1.0)
vent = st.radio("Viene rispettato il minimo di 8 l/s/persona di ventilazione naturale?", ["Sì", "No"], index = None, horizontal = True)   
retrofitCaso = st.radio("Selezionare eventuali interventi di retrofit effettuati", ["Nessun intervento", "Coibentazione pareti", "Coibentazione tetto", "Serramenti doppi"], index = None, horizontal = True)

button = st.toggle("Carica")
if not button:
    st.stop()

if supVetrata <= 13:
    WFR = 12
elif supVetrata > 13 and supVetrata <= 15:
    WFR = 14.000000000000002
elif supVetrata > 15 and supVetrata <= 17:
    WFR = 16
elif supVetrata > 17 and supVetrata <= 19:
    WFR = 18
elif supVetrata > 19 and supVetrata <= 21:
    WFR = 20
elif supVetrata > 21:
    WFR = 22

if g < 0.5:
    SHGC = 0.3
    valore = "basso"
else:
    SHGC = 0.9
    valore = "alto"
    
if vent == "Sì":
    vent = "8 l/s/pers"
else:
    vent = "1.2 ACH"

st.write("Soluzione per scuola in zona climatica {}, con WFR {}%, g value {} e {}".format(climatic_zone, WFR, valore, retrofitCaso))
st.write("Indicare per ogni gruppo il numero di aule, la posizione e l'orientamento.")

numero_df = pd.DataFrame(columns = ["numero", "nome", "floor", "orient", "retrofit"], index = range(number_of_types))

comfort_bands = pd.DataFrame(columns = [0, 1, 2, 3, 4], index = range(number_of_types))

distribution1 = pd.DataFrame(columns = ["non heating", "school non heating"], index = range(number_of_types))
distribution2 = pd.DataFrame(columns = ["non heating", "school non heating"], index = range(number_of_types))
tot1 = pd.DataFrame(columns = ["non heating", "school non heating"], index = range(number_of_types))
tot2 = pd.DataFrame(columns = ["non heating", "school non heating"], index = range(number_of_types))

tm52 = pd.DataFrame(columns = ["C1", "C2", "C3", "TOT"], index = range(number_of_types))

heat_stress = pd.DataFrame(columns = ["Giorni di stress termico totali", "Giorni di stress termico periodo scolastico non riscaldato"], index = range(number_of_types))
heat_stress_tot = pd.DataFrame(columns = ["Giorni di stress termico totali", "Giorni di stress termico periodo scolastico non riscaldato"], index = range(number_of_types))

for gruppo in range(number_of_types):
    st.subheader("\nGruppo di aule {}".format(gruppo+1), divider = True)
    if gruppo == number_of_types-1:
        numero = numeroAULE
        st.write("Numero di aule che appartengono al gruppo {}: {}".format(gruppo+1, numero))
    else:
        numero = st.slider("Selezionare il numero di aule che appartengono al gruppo di aule {}".format(gruppo+1), 0, numeroAULE)
    
    piano = st.radio("Selezionare il piano del gruppo di aule {}".format(gruppo+1), ["Terra", "Medio", "Ultimo"], index = None, horizontal = True)
    pos = st.radio("Selezionare la posizione del gruppo di aule {}".format(gruppo+1), ["Centrale", "Angolare"], index = None, horizontal = True)
    card = st.radio("Selezionare l'orientamento del gruppo di aule {}".format(gruppo+1), ["Sud", "Ovest", "Nord", "Est"], index = None, horizontal = True)
    
    button1 = st.toggle("Carica", key = "Carica{}".format(gruppo))
    if not button1:
        st.stop()
        
    numeroAULE = numeroAULE - numero
    numero_df.loc[gruppo, "nome"] = "Aule al piano {} {} esposte a {}".format(piano, pos, card) 
    numero_df.loc[gruppo, "numero"] = numero

    if piano == "Terra":
        floor = "G"
    elif piano == "Medio":
        floor = "M"
    elif piano == "Ultimo":
        floor = "T"
    
    if pos == "Centrale":
        floor = floor + "-M"
    elif pos == "Angolare":
        floor = floor + "-C"
    
    if card == "Sud":
        orient = 0
    elif card == "Ovest":
        orient = 90
    elif card == "Nord":
        orient = 180
    elif card == "Est":
        orient = 270
        
    if retrofitCaso == "Nessun intervento":
        retrofit = "BASE"
    elif retrofitCaso == "Coibentazione pareti":
        retrofit = "WALL"
    elif retrofitCaso == "Coibentazione tetto" and floor[0] == "T":
        retrofit = "ROOF"
    elif retrofitCaso == "Serramenti doppi":
        retrofit = "WINDOW"   
    
    numero_df.loc[gruppo, "floor"] = floor
    numero_df.loc[gruppo, "orient"] = orient
    numero_df.loc[gruppo, "retrofit"] = retrofit

# %% Read files
st.subheader("Caricamento dei dati", divider = True)
st.write("Tempo stimato: {} min {} sec".format(math.floor(number_of_types*20/60), round(number_of_types*20%60)))

import requests

# ── Zenodo settings ──────────────────────────────────────────────────────────
ZENODO_URLS = {
    "RISULTATI-base-Corner": "https://zenodo.org/records/20383573/files",
    "RISULTATI-base-Middle": "https://zenodo.org/records/20383688/files",
    "RISULTATI-sh00":        "https://zenodo.org/records/20383414/files",
    "RISULTATI-sh45":        "https://zenodo.org/records/20383336/files",
    "RISULTATI-night":       "https://zenodo.org/records/20383208/files",
    "RISULTATI-2050":        "https://zenodo.org/records/20383515/files",
    "RISULTATI-2080":        "https://zenodo.org/records/20383503/files",
    "RISULTATI-UHI":         "https://zenodo.org/records/20383533/files",
}

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".streamlit_cache", "scuole_results")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_folder_key(base_folder, floor):
    """For RISULTATI-base, pick Corner or Middle record based on floor position."""
    if base_folder == "RISULTATI-base":
        position = floor.split("-")[1]  # extracts "C" or "M" from e.g. "G-C"
        return f"RISULTATI-base-{('Corner' if position == 'C' else 'Middle')}"
    return base_folder

def get_file(folder, filename):
    folder_key = get_folder_key(folder, floor)
    local_path = os.path.join(CACHE_DIR, folder_key, filename)
    if not os.path.exists(local_path):
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        url = f"{ZENODO_URLS[folder_key]}/{filename}?download=1"
        st.toast(f"Downloading {filename}...")
        r = requests.get(url, timeout=300, stream=True)
        if r.status_code != 200:
            st.error(f"Could not download {filename} (error {r.status_code}). Check your Zenodo record.")
            st.stop()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_path


for gruppo in range(number_of_types):
    floor = numero_df["floor"][gruppo]
    orient = numero_df["orient"][gruppo] 
    retrofit = numero_df["retrofit"][gruppo]
    
    city, startNH, endNH, xgen, xfeb, xmar, xapr, xmay, xjun, xjul, xaug, xsep, xoct, xnov, xdec = climzone(climatic_zone)
    
    startSummer = "2025-06-15 00:00:00"
    endSummer = "2025-09-15 00:00:00"
    
    st.write("Caricamento dei dati - Gruppo di aule {}...".format(gruppo+1))
    
    # Folder
    folder = "local"  # kept as a placeholder, no longer used for paths
    temp_df_tot        = pd.read_excel(get_file("RISULTATI-base",  f"Temperatures-{city}-{floor}.xlsx"))
    scenarios_df_tot   = pd.read_excel(get_file("RISULTATI-base",  f"Scenarios-{city}-{floor}.xlsx"))
    dist_df_tot        = pd.read_excel(get_file("RISULTATI-base",  f"Dist-{city}-{floor}.xlsx"))
    
    temp_df_tot['ts'] = pd.Timestamp('2025-01-01 00:00:00') + pd.to_timedelta(temp_df_tot.index, unit='h')
    temp_df_tot["Month"] = temp_df_tot["ts"].dt.month
    temp_df_tot["Day"] = temp_df_tot["ts"].dt.day
    temp_df_tot["Weekday"] = temp_df_tot["ts"].dt.weekday  # Monday=0, Sunday=6
    temp_df_tot["Hour"] = temp_df_tot["ts"].dt.hour
    temp_df_tot = temp_df_tot.set_index("ts")
    
    if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
        caso = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
    elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
        caso = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
    elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
        caso = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
    elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
        caso = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
    
    temp_df = pd.concat([temp_df_tot[caso], temp_df_tot["Trm-{}".format(city)], temp_df_tot["Tmax-{}".format(city)], temp_df_tot["TmaxVent-{}".format(city)], temp_df_tot["Tout-{}".format(city)], temp_df_tot["Month"], temp_df_tot["Day"], temp_df_tot["Day"], temp_df_tot["Weekday"], temp_df_tot["Hour"]], axis=1)
    
    scenarios_df = scenarios_df_tot[(scenarios_df_tot["window_to_floor_ratio"] == WFR/100) & (scenarios_df_tot["building_orientation"] == orient) & (scenarios_df_tot["solar_heat_gain_coefficient"] == SHGC) & (scenarios_df_tot["THERMAL"] == retrofit) & (scenarios_df_tot["VENT"] == vent)]
    
    if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
    elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
    elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
    elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
    
    dist_df = pd.concat([dist_df_tot[dist_df_tot["Unnamed: 0"] == "bins"], dist_df_tot[dist_df_tot["Unnamed: 0"] == casoDist], dist_df_tot[dist_df_tot["Unnamed: 0"] == "{} VENT".format(casoDist)]])

        
    #%% Display results - comfort bands        
    plt.rcParams.update({'font.size': 10})
    periodCase = pd.DataFrame(index=[0, 1, 2, 3, 4], columns=["C1", "C2", "C3", "Overheating", "C1_VENT", "C2_VENT", "C3_VENT", "Overheating_VENT", "low", "lowBand3", "lowBand2", "Band1", "highBand2", "highBand3", "high", "lowVent", "lowBand3Vent", "lowBand2Vent", "Band1Vent", "highBand2Vent", "highBand3Vent", "highVent"])
    
    P1_mask = (temp_df.index >= "2025-01-01 00:00:00") & (temp_df.index < startNH)
    P2_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer)
    P3_mask = (temp_df.index >= startSummer) & (temp_df.index < endSummer)
    P4_mask = (temp_df.index >= endSummer) & (temp_df.index < endNH)
    P5_mask = (temp_df.index >= endNH) & (temp_df.index <= "2025-12-31 23:00:00")
    
    temp_df_P1 = temp_df.loc[P1_mask].copy()
    temp_df_P2 = temp_df.loc[P2_mask].copy()
    temp_df_P3 = temp_df.loc[P3_mask].copy()
    temp_df_P4 = temp_df.loc[P4_mask].copy()
    temp_df_P5 = temp_df.loc[P5_mask].copy()
    
    temp_list = [temp_df_P1, temp_df_P2, temp_df_P3, temp_df_P4, temp_df_P5]
    nomi = ["Inizio dell'anno - \nspegnimento \nriscaldamento", "Spegnimento \nriscaldamento - \nfine della scuola",
            "Fine - inizio \ndella scuola", "Inizio della scuola - \naccensione \nriscaldamento", "Accensione \nriscaldamento - \nfine dell'anno"]

    lista = []
    
    for periodo in [0, 1, 2, 3, 4]:
        nomePeriodo = nomi[periodo]
        temp_period = temp_list[periodo]
    
        temp_period_case = temp_period[caso]
        temp_out_period = temp_period["Tout-{}".format(city)].values
    
        temp, Trm, Tmax, percentC1, percentC2, percentC3, overheating, Tmax_vent, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, dist_df_period, low, lowBand3, lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent = exceeding_hours_TM52(temp_out_period, temp_period_case, climatic_zone)
    
        # Save results
        lista = lista + [high]
        
    comfort_bands.loc[gruppo] = lista
    comfort_bands = comfort_bands.astype(float)
         
    #%% Distribution of temperatures T > Tmax and T>Tmax+2
    
    # Number of days outside comfort zone and some data
    occupied_months = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]        # May, June, July, September
    occupied_weekdays = [0, 1, 2, 3, 4]   # Monday to Friday
    occupied_hours = range(8, 18)

    temp_df["Occupied"] = (temp_df["Month"].isin(occupied_months) & temp_df["Weekday"].isin(occupied_weekdays) & temp_df["Hour"].isin(occupied_hours))

    # ALl non heating period
    nonheat_mask = (temp_df.index >= startNH) & (temp_df.index < endNH)
    df_nonheat = temp_df.loc[nonheat_mask].copy()

    df_occ = df_nonheat[df_nonheat["Occupied"]].copy()
    dist = np.where(df_occ[caso] > df_occ["Tmax-{}".format(city)], df_occ[caso] - df_occ["Tmax-{}".format(city)], 0)
    distVent = np.where(df_occ[caso] > df_occ["TmaxVent-{}".format(city)], df_occ[caso] - df_occ["TmaxVent-{}".format(city)], 0)

    bins = np.arange(0, 11, 1).tolist()
    counts1, bins = np.histogram(dist)

    # School non heating period
    schoolNH_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer) | (temp_df.index > endSummer) & (temp_df.index < endNH)
    df_schoolNH = temp_df.loc[schoolNH_mask].copy()

    df_occ = df_schoolNH[df_schoolNH["Occupied"]].copy()
    dist = np.where(df_occ[caso] > df_occ["Tmax-{}".format(city)], df_occ[caso] - df_occ["Tmax-{}".format(city)], 0)
    distVent = np.where(df_occ[caso] > df_occ["TmaxVent-{}".format(city)], df_occ[caso] - df_occ["TmaxVent-{}".format(city)], 0)

    bins = np.arange(0, 11, 1).tolist()
    counts3, bins = np.histogram(dist)

    uno = round(counts1.sum()-counts1[0])
    due = round(counts1.sum())
    tre = round(counts3.sum()-counts3[0])
    quattro = round(counts3.sum())
    cinque = round(counts1.sum()-counts1[0]-counts1[1]-counts1[2])
    sei = round(counts1.sum())
    sette = round(counts3.sum()-counts3[0]-counts3[1]-counts3[2])
    otto = round(counts3.sum())
        
    distribution1.loc[gruppo] = [uno, tre]
    distribution2.loc[gruppo] = [cinque, sette]
    tot1.loc[gruppo] = [due, quattro]
    tot2.loc[gruppo] = [sei, otto]
    
    distribution1 = distribution1.astype(float)
    distribution2 = distribution2.astype(float)
    tot1 = tot1.astype(float)
    tot2 = tot2.astype(float)
    
    #%% TM52
    c1 = scenarios_df["C1"][scenarios_df.index[0]]
    c2 = scenarios_df["C2"][scenarios_df.index[0]]
    c3 = scenarios_df["C3"][scenarios_df.index[0]]
    
    if (c1 == 0) | (c2 == 0) | (c3 == 0):
        tot = 0
    else:
        tot = 100
    
    tm52.loc[gruppo] = [c1, c2, c3, tot]
    
    #%% Heat stress days
    
    # Days in which ventilation is feasible = days in which at ALL hours the temperature outside is lower than the indoor one and lower than the threshold
    vent_df = pd.DataFrame(0, index=temp_df.index, columns=temp_df.columns)

    vent_df.loc[(temp_df["Tout-{}".format(city)] < temp_df["Tmax-{}".format(city)] - 7) & (temp_df["Tout-{}".format(city)] < temp_df[caso]), caso] = 1

    vent_daily = vent_df.resample("1440min").sum()
    temp_daily = temp_df.resample("1440min").max()

    heat_df = pd.DataFrame(0, index=temp_daily.index, columns=temp_daily.columns)
    heat_df = heat_df.drop(columns=["Trm-{}".format(city), "Tmax-{}".format(city), "TmaxVent-{}".format(city), "Tout-{}".format(city)])
    heat_df_vent = heat_df.copy()

    # Share of days in which indoor temperature is above the threshold and ventilation is not feasible, or in which Trm is above 30°C (limit of the adaptive chart)
    heat_df.loc[((temp_daily[caso] > temp_daily["Tmax-{}".format(city)]) |
                 (temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[caso] < 24), caso] = 1
    heat_df_vent.loc[((temp_daily[caso] > temp_daily["TmaxVent-{}".format(city)]) |
                      (temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[caso] < 24), caso] = 1

    share = heat_df.sum(axis=0) / 365 * 100

    # At least 3 consecutive days to be considered heat wave
    heat_df_updated = heat_df.copy()
    heat_df_vent_updated = heat_df_vent.copy()

    for day in heat_df.index:
        if (day == pd.Timestamp('2025-01-01 00:00:00')) | (day == pd.Timestamp('2025-01-02 00:00:00')) | (day == pd.Timestamp('2025-12-30 00:00:00')) | (day == pd.Timestamp('2025-12-31 00:00:00')):
            ieri = 0
            laltroieri = 0
            oggi = heat_df[caso][day]
            domani = 0
            dopodomani = 0
        else:
            laltroieri = heat_df[caso][day - pd.to_timedelta(2, unit='D')]
            ieri = heat_df[caso][day - pd.to_timedelta(1, unit='D')]
            oggi = heat_df[caso][day]
            domani = heat_df[caso][day + pd.to_timedelta(1, unit='D')]
            dopodomani = heat_df[caso][day + pd.to_timedelta(2, unit='D')]

        if oggi == 1:
            if ((domani == 1) & (dopodomani == 1)) | ((ieri == 1) & (laltroieri == 1)) | ((ieri == 1) & (domani == 1)):
                heat_df_updated.loc[day, caso] = 1
            else:
                heat_df_updated.loc[day, caso] = 0

    for day in heat_df_vent.index:
        if (day == pd.Timestamp('2025-01-01 00:00:00')) | (day == pd.Timestamp('2025-01-02 00:00:00')) | (day == pd.Timestamp('2025-12-30 00:00:00')) | (day == pd.Timestamp('2025-12-31 00:00:00')):
            ieri = 0
            laltroieri = 0
            oggi = heat_df_vent[caso][day]
            domani = 0
            dopodomani = 0
        else:
            laltroieri = heat_df_vent[caso][day - pd.to_timedelta(2, unit='D')]
            ieri = heat_df_vent[caso][day - pd.to_timedelta(1, unit='D')]
            oggi = heat_df_vent[caso][day]
            domani = heat_df_vent[caso][day + pd.to_timedelta(1, unit='D')]
            dopodomani = heat_df_vent[caso][day + pd.to_timedelta(2, unit='D')]

        if oggi == 1:
            if ((domani == 1) & (dopodomani == 1)) | ((ieri == 1) & (laltroieri == 1)) | ((ieri == 1) & (domani == 1)):
                heat_df_vent_updated.loc[day, caso] = 1
            else:
                heat_df_vent_updated.loc[day, caso] = 0

    heat_df_updated["Trm"] = temp_daily["Trm-{}".format(city)]
    share_update = heat_df_updated.sum(axis=0) / 365 * 100
    share_vent_update = heat_df_vent_updated.sum(axis=0) / 365 * 100


    numeroTOT = round(heat_df_updated.sum(axis=0)[caso])
    schoolNH_mask_daily = (heat_df_updated.index >= startNH) & (heat_df_updated.index < startSummer) | (heat_df_updated.index > endSummer) & (heat_df_updated.index < endNH)
    heat_df_scuola = heat_df_updated.loc[schoolNH_mask_daily].copy()
    numeroESTATE = round(heat_df_scuola.sum(axis=0)[caso])
    
    heat_stress.loc[gruppo] = [numeroTOT, numeroESTATE]
    heat_stress = heat_stress.astype(float)
    heat_stress_tot.loc[gruppo] = [365, heat_df_scuola.shape[0]]
    
#%% Plots

st.subheader("\nRisultati", divider = True)

def numeri(max_valRow, max_valCol, df, ax):
    for j in range(max_valRow):
        for k in range(max_valCol):
            c = df[df.columns[j]][df.index[k]]
            ax.text(j, k, "{}%".format(str(round(c, 1))),
                     va='center', ha='center', fontsize=12)

def numeri2(max_valRow, max_valCol, df, dftot, ax):
    for j in range(max_valRow):
        for k in range(max_valCol):
            c = df[df.columns[j]][df.index[k]]
            t = dftot[dftot.columns[j]][dftot.index[k]]
            ax.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=12)

def truefalse(max_valRow, max_valCol, df, ax):
    for j in range(max_valRow):
        for k in range(max_valCol):
            ax.text(j, k, "No overheating" if tot["TOT"].iloc[k] == 0 else "Overheating", va='center', ha='center', fontsize=8)
            
def wrap_labels(df, ax, width):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width, break_long_words=False))
    ax.set_xticklabels(df.columns, rotation=0, fontsize=8)
    ax.set_yticklabels(numero_df["nome"], fontsize=8)
    
def wrap_labels2(df, ax, width):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width, break_long_words=False))
    ax.set_xticklabels(df.columns, rotation=0, fontsize=8)
    ax.set_yticklabels("", fontsize=8)
    
#%% Comfort bands
st.write("Percentuale di ore con T > Tmax nei diversi periodi dell'anno")
comfort_bands.columns = ["Inizio dell'anno - \nspegnimento \nriscaldamento", "Spegnimento \nriscaldamento - \nfine della scuola",
        "Fine - inizio \ndella scuola", "Inizio della scuola - \naccensione \nriscaldamento", "Accensione \nriscaldamento - \nfine dell'anno"]

fig, ax = plt.subplots()
fig.set_figheight(6)
fig.set_figwidth(9)

im = ax.matshow(comfort_bands, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, 100])
ax.set_xticks(np.arange(len(comfort_bands.columns)), minor=False)
ax.set_yticks(np.arange(len(comfort_bands.index)), minor=False)
ax.xaxis.tick_top()
ax.grid(which="minor", c='black', ls=':', lw='0.4')
ax.set_xticks([x-0.5 for x in range(1, len(comfort_bands.columns))], minor=True)
ax.set_yticks([y-0.5 for y in range(1, len(comfort_bands.index))], minor=True)
wrap_labels(comfort_bands, ax, 5)

numeri(5, number_of_types, comfort_bands, ax)

st.pyplot(fig)

#%% Distribution
#print("La scuola presenta {} aule in rischio di overheating secondo la TM52".format())
fig, ax = plt.subplots()
fig.set_figheight(6)
fig.set_figwidth(9)

massimo = min((distribution1/tot1).values.max(), 0.30)

ax.text(0.5, -1.05, "N° di ore con T>Tmax / N° di ore totali", ha = "center")
im = ax.matshow(distribution1/tot1, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax.set_xticks(np.arange(len(distribution1.columns)), minor=False)
ax.set_yticks(np.arange(len(distribution1.index)), minor=False)
ax.xaxis.tick_top()
ax.grid(which="minor", c='black', ls=':', lw='0.4')
ax.set_xticks([x-0.5 for x in range(1, len(distribution1.columns))], minor=True)
ax.set_yticks([y-0.5 for y in range(1, len(distribution1.index))], minor=True)
wrap_labels(distribution1, ax, 5)
numeri2(2, number_of_types, distribution1, tot1, ax)
st.pyplot(fig)

fig, ax = plt.subplots()
fig.set_figheight(6)
fig.set_figwidth(9)
ax.text(0.5, -1.05, "N° di ore con T>Tmax+2°C / N° di ore totali", ha = "center")
im = ax.matshow(distribution2/tot2, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax.set_xticks(np.arange(len(distribution2.columns)), minor=False)
ax.set_yticks(np.arange(len(distribution2.index)), minor=False)
ax.xaxis.tick_top()
ax.grid(which="minor", c='black', ls=':', lw='0.4')
ax.set_xticks([x-0.5 for x in range(1, len(distribution2.columns))], minor=True)
ax.set_yticks([y-0.5 for y in range(1, len(distribution2.index))], minor=True)
wrap_labels(distribution2, ax, 5)
numeri2(2, number_of_types, distribution2, tot2, ax)
st.pyplot(fig)

#%% TM52
somma = (numero_df["numero"]*tm52["TOT"]/100).sum()
st.write("La scuola presenta {} / {} aule in rischio di overheating secondo la TM52".format(round(somma), (numero_df["numero"]).sum()))
fig, (ax1,ax2) = plt.subplots(1,2)
fig.set_figheight(6)
fig.set_figwidth(9)

criteri = pd.concat([tm52["C1"], tm52["C2"], tm52["C3"]], axis=1)
criteri = criteri.astype(float)
im = ax1.matshow(criteri, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, 100])
ax1.set_xticks(np.arange(len(criteri.columns)), minor=False)
ax1.set_yticks(np.arange(len(criteri.index)), minor=False)
ax1.xaxis.tick_top()
ax1.grid(which="minor", c='black', ls=':', lw='0.4')
ax1.set_xticks([x-0.5 for x in range(1, len(criteri.columns))], minor=True)
ax1.set_yticks([y-0.5 for y in range(1, len(criteri.index))], minor=True)
wrap_labels(criteri, ax1, 5)

tot = pd.DataFrame(tm52["TOT"])
tot = tot.astype(float)
im = ax2.matshow(tot, cmap="RdYlGn_r", interpolation="none", aspect = 0.25/3)
im.norm.autoscale([0, 100])
ax2.set_xticks(np.arange(len(tot.columns)), minor=False)
ax2.set_yticks(np.arange(len(tot.index)), minor=False)
ax2.xaxis.tick_top()
ax2.grid(which="minor", c='black', ls=':', lw='0.4')
ax2.set_xticks([x-0.5 for x in range(1, len(tot.columns))], minor=True)
ax2.set_yticks([y-0.5 for y in range(1, len(tot.index))], minor=True)
wrap_labels2(tot, ax2, 5)

numeri(3, number_of_types, criteri, ax1)
truefalse(1, number_of_types, tot, ax2)

st.pyplot(fig)

#%% Heat stress
st.write("Giorni totali di stress termico e giorni di stress termico per il periodo scolastico di spegnimento del riscaldamento")
fig, ax = plt.subplots()
fig.set_figheight(6)
fig.set_figwidth(9)

massimoHeatStress = min((heat_stress.values/heat_stress_tot.values).max(), 0.30)

im = ax.matshow((heat_stress.values/heat_stress_tot.values).astype(float), cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimoHeatStress])
ax.set_xticks(np.arange(len(heat_stress.columns)), minor=False)
ax.set_yticks(np.arange(len(heat_stress.index)), minor=False)
ax.xaxis.tick_top()
ax.grid(which="minor", c='black', ls=':', lw='0.4')
ax.set_xticks([x-0.5 for x in range(1, len(heat_stress.columns))], minor=True)
ax.set_yticks([y-0.5 for y in range(1, len(heat_stress.index))], minor=True)
wrap_labels(heat_stress, ax, 5)

numeri2(2, number_of_types, heat_stress, heat_stress_tot, ax)

st.pyplot(fig)

#%% Overall results
        
ratio = distribution2/tot2 
ratio2 = heat_stress/heat_stress_tot

# Stagioni intermedie
# Aule
rischio = pd.DataFrame(0, columns = ["comfort bands", "dist", "tm52", "heat stress", "finale", "rate"], index = range(number_of_types))
      
rischio["comfort bands"].mask((comfort_bands["Spegnimento \nriscaldamento - \nfine della scuola"] > 5) | (comfort_bands["Inizio della scuola - \naccensione \nriscaldamento"] > 5), 1, inplace=True)
rischio["dist"].mask((ratio["school non heating"] > 0.05), 1, inplace=True)
rischio["tm52"].mask((tm52['TOT'] == 100), 1, inplace=True)
rischio["heat stress"].mask((ratio2["Giorni di stress termico periodo scolastico non riscaldato"] > 0.1), 1, inplace=True)

rischio["finale"].mask((rischio["comfort bands"] == 1) | (rischio["dist"] == 1) & (rischio["tm52"] == 1) | (rischio["heat stress"] == 1), 0.5, inplace=True)
rischio["finale"].mask((rischio["comfort bands"] == 1) & (rischio["dist"] == 1) & (rischio["tm52"] == 1) & (rischio["heat stress"] == 1), 1, inplace=True)
rischio["finale"].mask((rischio["comfort bands"] == 1) & (rischio["dist"] == 0), 0.5, inplace=True)
rischio["finale"].mask((rischio["tm52"] == 0), 0, inplace=True)

rischio["rate"].mask(rischio["finale"] == 1, "alto", inplace=True)
rischio["rate"].mask(rischio["finale"] == 0.5, "medio", inplace=True)
rischio["rate"].mask(rischio["finale"] == 0, "basso", inplace=True)

for gruppo in range(number_of_types):
    if rischio["rate"][gruppo] == "alto":
        st.write("Group {}: {} {} --> rischio di overheating :red[{}] nelle stagioni intermedie".format(gruppo+1, numero_df["numero"][gruppo], numero_df["nome"][gruppo], rischio["rate"][gruppo]))
    elif rischio["rate"][gruppo] == "medio":
        st.write("Group {}: {} {} --> rischio di overheating :yellow[{}] nelle stagioni intermedie".format(gruppo+1, numero_df["numero"][gruppo], numero_df["nome"][gruppo], rischio["rate"][gruppo]))      
    elif rischio["rate"][gruppo] == "basso":
        st.write("Group {}: {} {} --> rischio di overheating :green[{}] nelle stagioni intermedie".format(gruppo+1, numero_df["numero"][gruppo], numero_df["nome"][gruppo], rischio["rate"][gruppo]))

# Scuola
aule_tot = numero_df["numero"].sum()
aule_calde = 0

for caso in numero_df.index:
    if rischio["rate"][caso] == "alto":
        aule_calde = aule_calde + numero_df["numero"][caso]
        
if (aule_calde / aule_tot) > 0.25:
    rischioTOT = "alto"
else:
    rischioTOT = "basso"

if rischioTOT == "alto":
    st.subheader("La scuola è esposta a rischio :red[alto] di overheating nelle stagioni intermedie")
elif rischioTOT == "basso":
    st.subheader("La scuola è esposta a rischio :green[basso] di overheating nelle stagioni intermedie")
else:
    st.subheader("La scuola è esposta a rischio :yellow[medio] di overheating nelle stagioni intermedie")
    
# Estate
# Aule
rischio = pd.DataFrame(0, columns = ["comfort bands", "dist", "tm52", "heat stress", "finale", "rate"], index = range(number_of_types))

rischio["comfort bands"].mask((comfort_bands["Fine - inizio \ndella scuola"] > 5), 1, inplace=True)
rischio["dist"].mask((ratio["non heating"] > 0.05), 1, inplace=True)
rischio["tm52"].mask((tm52['TOT'] == 100), 1, inplace=True)
rischio["heat stress"].mask((ratio2["Giorni di stress termico totali"] > 0.1), 1, inplace=True)

rischio["finale"].mask((rischio["comfort bands"] == 1) | (rischio["dist"] == 1) & (rischio["tm52"] == 1) | (rischio["heat stress"] == 1), 0.5, inplace=True)
rischio["finale"].mask((rischio["comfort bands"] == 1) & (rischio["dist"] == 1) & (rischio["tm52"] == 1) & (rischio["heat stress"] == 1), 1, inplace=True)
rischio["finale"].mask((rischio["comfort bands"] == 1) & (rischio["dist"] == 0), 0.5, inplace=True)
rischio["finale"].mask((rischio["tm52"] == 0), 0, inplace=True)

rischio["rate"].mask(rischio["finale"] == 1, "alto", inplace=True)
rischio["rate"].mask(rischio["finale"] == 0.5, "medio", inplace=True)
rischio["rate"].mask(rischio["finale"] == 0, "basso", inplace=True)

for gruppo in range(number_of_types):
    if rischio["rate"][gruppo] == "alto":
        st.write("Group {}: {} {} --> rischio di overheating :red[{}] in estate".format(gruppo+1, numero_df["numero"][gruppo], numero_df["nome"][gruppo], rischio["rate"][gruppo]))
    elif rischio["rate"][gruppo] == "medio":
        st.write("Group {}: {} {} --> rischio di overheating :yellow[{}] in estate".format(gruppo+1, numero_df["numero"][gruppo], numero_df["nome"][gruppo], rischio["rate"][gruppo]))      
    elif rischio["rate"][gruppo] == "basso":
        st.write("Group {}: {} {} --> rischio di overheating :green[{}] in estate".format(gruppo+1, numero_df["numero"][gruppo], numero_df["nome"][gruppo], rischio["rate"][gruppo]))

# Scuola
aule_tot = numero_df["numero"].sum()
aule_calde = 0

for caso in numero_df.index:
    if rischio["rate"][caso] == "alto":
        aule_calde = aule_calde + numero_df["numero"][caso]
        
if (aule_calde / aule_tot) < 0.25:
    rischioTOT = "basso"
elif (aule_calde / aule_tot) < 3/5:
    rischioTOT = "medio"
else: 
    rischioTOT = "alto"

if rischioTOT == "alto":
    st.subheader("La scuola è esposta a rischio :red[alto] di overheating e non può essere usata in estate")
elif rischioTOT == "basso":
    st.subheader("La scuola è esposta a rischio :green[basso] di overheating e può essere usata con un livello accettabile di comfort per uso sporadico in estate")
else:
    st.subheader("La scuola è esposta a rischio :yellow[medio] di overheating e può essere usata in modo discontinuo con bassa affluenza in estate")
    

st.write("Per comparare diverse possibilità di mitigazione della condizione dei diversi gruppi di aule, utilizzare il tool per le aule")