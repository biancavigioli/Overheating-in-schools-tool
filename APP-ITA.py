import streamlit as st 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
import os
import sys


# %% Color palettes
blue = sns.mpl_palette("Blues", 48)
red = sns.mpl_palette("Reds", 48)
green = sns.mpl_palette("Greens", 48)

#%% Inputs

st.title("Tool per l'identificazione della condizione di overheating nelle aule scolastiche")
st.write("Questo tool permette di analizzare il potenziale di overheating delle aule scolastiche, sulla base della localizzazione e delle caratteristiche geometriche, di involucro e di ventilazione")

climatic_zone = st.radio("Selezionare la zona climatica", ["A", "B", "C", "D", "E", "F"], index = None, horizontal = True)
piano = st.radio("Selezionare il piano dell'aula", ["Terra", "Medio", "Ultimo"], index = None, horizontal = True)
pos = st.radio("Selezionare la posizione dell'aula", ["Centrale", "Angolare"], index = None, horizontal = True)
card = st.radio("Selezionare l'orientamento dell'aula", ["Sud", "Ovest", "Nord", "Est"], index = None, horizontal = True)   
supVetrata = st.slider("Indicare il rapporto superficie vetrata / superficie del pavimento in %", 0, 100)   
g = st.slider("Indicare il fattore solare (g-value) dei vetri (basso = vetri performanti; alto = vetri chiari)", 0.0, 1.0)
vent = st.radio("Viene rispettato il minimo di 8 l/s/persona di ventilazione naturale?", ["Sì", "No"], index = None, horizontal = True)   
retrofitCaso = st.radio("Selezionare eventuali interventi di retrofit effettuati", ["Nessun intervento", "Coibentazione pareti", "Coibentazione tetto", "Serramenti doppi"], index = None, horizontal = True)

button = st.toggle("Carica")
if not button:
    st.stop()

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

if retrofitCaso == "Nessun intervento":
    retrofit = "BASE"
elif retrofitCaso == "Coibentazione pareti":
    retrofit = "WALL"
elif retrofitCaso == "Coibentazione tetto" and floor[0] == "T":
    retrofit = "ROOF"
elif retrofitCaso == "Serramenti doppi":
    retrofit = "WINDOW"
    
st.write("Soluzione per classe in zona climatica {}, al piano {} {}, esposta a {}, con WFR {}%, g value {}, e {}".format(climatic_zone, piano, pos, card, WFR, valore, retrofitCaso))

# %% Read files
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

startSummer = "2025-06-15 00:00:00"
endSummer = "2025-09-15 00:00:00"

st.write("Caricamento dei dati...")
st.write("Tempo stimato: 20 sec")

# Folder
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

# ── Load data ────────────────────────────────────────────────────────────────
folder = "local"  # kept as a placeholder, no longer used for paths
temp_df_tot        = pd.read_excel(get_file("RISULTATI-base",  f"Temperatures-{city}-{floor}.xlsx"))
scenarios_df_tot   = pd.read_excel(get_file("RISULTATI-base",  f"Scenarios-{city}-{floor}.xlsx"))
dist_df_tot        = pd.read_excel(get_file("RISULTATI-base",  f"Dist-{city}-{floor}.xlsx"))

# ── Base data ────────────────────────────────────────────────────────────────
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

# %% Function
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


# %% Display results - comfort bands
st.subheader("Risultati", divider = True)
st.write("Percentuale di ore nelle categorie di comfort suddivise per periodi sulla base dell'accensione del riscaldamento e sulle vacanze estive.")
         
plt.rcParams.update({'font.size': 10})
periodCase = pd.DataFrame(index=[0, 1, 2, 3, 4], columns=["C1", "C2", "C3", "Overheating", "C1_VENT", "C2_VENT", "C3_VENT", "Overheating_VENT", "low", "lowBand3",
                          "lowBand2", "Band1", "highBand2", "highBand3", "high", "lowVent", "lowBand3Vent", "lowBand2Vent", "Band1Vent", "highBand2Vent", "highBand3Vent", "highVent"])

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

fig, ax = plt.subplots()
fig.set_figheight(6)
fig.set_figwidth(9)
w = 0.5

for periodo in [0, 1, 2, 3, 4]:
    nomePeriodo = nomi[periodo]
    temp_period = temp_list[periodo]

    temp_period_case = temp_period[caso]
    temp_out_period = temp_period["Tout-{}".format(city)].values

    temp, Trm, Tmax, percentC1, percentC2, percentC3, overheating, Tmax_vent, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, dist_df_period, low, lowBand3, lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent = exceeding_hours_TM52(
        temp_out_period, temp_period_case, climatic_zone)

    # Save results
    lista = [percentC1, percentC2, percentC3, overheating, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, low, lowBand3,
             lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent]
    periodCase.loc[periodo] = lista

ax.bar([0, 1, 2, 3, 4], periodCase["low"], w, color="#90e0ef", label="T<Tmin")
ax.bar([0, 1, 2, 3, 4], periodCase["lowBand3"],  w,
       bottom=periodCase["low"], color="#ddead1", label="III fascia di comfort")
ax.bar([0, 1, 2, 3, 4], periodCase["lowBand2"],  w, bottom=periodCase["lowBand3"] +
       periodCase["low"], color="#95bb72", label="II fascia di comfort")
ax.bar([0, 1, 2, 3, 4], periodCase["Band1"],  w, bottom=periodCase["lowBand2"] +
       periodCase["lowBand3"] + periodCase["low"], color="#4b6043", label="I fascia di comfort")
ax.bar([0, 1, 2, 3, 4], periodCase["highBand2"],  w, bottom=periodCase["Band1"] +
       periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#95bb72")
ax.bar([0, 1, 2, 3, 4], periodCase["highBand3"],  w, bottom=periodCase["highBand2"] + periodCase["Band1"] +
       periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#ddead1")
ax.bar([0, 1, 2, 3, 4], periodCase["high"],  w, bottom=periodCase["highBand3"] + periodCase["highBand2"] +
       periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#f69697", label="T>Tmax")
handles, labels = ax.get_legend_handles_labels()

ax.set_xticks([0, 1, 2, 3, 4], nomi)
ypisl = -15
ax.text(xgen, ypisl, "GEN", color=sns.mpl_palette("Set2")[2], ha="center")
ax.text(xfeb, ypisl, "FEB", color=sns.mpl_palette("Set2")[2], ha="center")
ax.text(xmar, ypisl, "MAR", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xapr, ypisl, "APR", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xmay, ypisl, "MAG", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xjun, ypisl, "GIU", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xjul, ypisl, "LUG", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xaug, ypisl, "AGO", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xsep, ypisl, "SET", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xoct, ypisl, "OTT", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xnov, ypisl, "NOV", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xdec, ypisl, "DIC", color=sns.mpl_palette("Set2")[2], ha="center")

ax.set_ylim(0, 100)
ax.text(-1, 50, "Percentuale di ore in ciascuna fascia di comfort [%]", rotation="vertical", va="center")

fig.legend(handles[:5], labels[:5], loc='upper center', ncol=7)

st.pyplot(fig)

#%% Display results - temperature distribution
st.write("Distribuzione di frequenza delle temperature sopra alla Tmax. Dati riferiti al periodo di spegnimento del riscaldamento nelle ore occupate.")

plt.rcParams.update({'font.size': 8})

fig, axs = plt.subplot_mosaic([['dist', 'scritte1'], ['dist', 'scritte2']], layout='constrained')
ax1 = axs["dist"]
ax2 = axs["scritte1"]
ax3 = axs["scritte2"]

fig.set_figheight(6)
fig.set_figwidth(9)

bins = dist_df[dist_df["Unnamed: 0"] == "bins"].drop(columns=["Unnamed: 0"]).values.flatten()
new_bins = [x+33 for x in bins]

ax1.plot(dist_df[dist_df["Unnamed: 0"] == "bins"].drop(columns=["Unnamed: 0"]).values.flatten(), dist_df[dist_df["Unnamed: 0"] == casoDist].drop(columns=["Unnamed: 0"]).values.flatten()*100, label="Velocità aria non aumentata", color=red[24])
ax1.axvspan(2, 9, alpha = 0.3, color = red[24], label = "Estremamente inaccettabile")
ax1.axhspan(95, 100, xmin = 0, xmax = 2/9, alpha = 0.3, color=green[24], label = "Trascurabilmente inaccettabile")
ax1.plot(dist_df[dist_df["Unnamed: 0"] == "bins"].drop(columns=["Unnamed: 0"]).values.flatten(), dist_df[dist_df["Unnamed: 0"] == "{} VENT".format(casoDist)].drop(columns=["Unnamed: 0"]).values.flatten()*100, label="Velocità aria aumentata", color=blue[24])
ax1.axhspan(0, 95, xmin = 0, xmax = 2/9, alpha = 0.3, color = red[12], label = "Inaccettabile")

ax1.xaxis.set_tick_params(labelbottom=True)
ax1.yaxis.set_tick_params(labelbottom=True)
ax1.set_ylim(0, 100)
ax1.set_yticks(np.arange(0, 101, 10))
ax1.set_xlim(0, 9)
ax1.set_xticks(range(0, 10))

ax1.set_xlabel("T - Tmax [°C]", ha='center')
ax1.set_ylabel("Frequenza cumulata [%]", va='center', rotation='vertical')
ax1.text(4.5, 103, "PERIODO NON RISCALDATO, ORE OCCUPATE", ha = "center", weight = "demi")

fig.legend(bbox_to_anchor = [0.43, 1.1], ncol=2, fontsize=8)

# Percentage of hours outside comfort bands
# Number of days outside comfort zone and some data
occupied_months = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]        # May, June, July, September
occupied_weekdays = [0, 1, 2, 3, 4]   # Monday to Friday
occupied_hours = range(8, 18)

temp_df["Occupied"] = (temp_df["Month"].isin(occupied_months) & temp_df["Weekday"].isin(occupied_weekdays) & temp_df["Hour"].isin(occupied_hours))

# ALl non heating period
nonheat_mask = (temp_df.index >= startNH) & (temp_df.index < endNH)
df_nonheat = temp_df.loc[nonheat_mask].copy()

df_occ = df_nonheat[df_nonheat["Occupied"]].copy()
dist = np.where(df_occ[caso] > df_occ["Tmax-{}".format(city)],
                df_occ[caso] - df_occ["Tmax-{}".format(city)], 0)
distVent = np.where(df_occ[caso] > df_occ["TmaxVent-{}".format(city)],
                    df_occ[caso] - df_occ["TmaxVent-{}".format(city)], 0)

bins = np.arange(0, 11, 1).tolist()
counts1, bins = np.histogram(dist)
counts2, bins = np.histogram(distVent)

# School non heating period
schoolNH_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer) | (temp_df.index > endSummer) & (temp_df.index < endNH)
df_schoolNH = temp_df.loc[schoolNH_mask].copy()

df_occ = df_schoolNH[df_schoolNH["Occupied"]].copy()
dist = np.where(df_occ[caso] > df_occ["Tmax-{}".format(city)],
                df_occ[caso] - df_occ["Tmax-{}".format(city)], 0)
distVent = np.where(df_occ[caso] > df_occ["TmaxVent-{}".format(city)],
                    df_occ[caso] - df_occ["TmaxVent-{}".format(city)], 0)

bins = np.arange(0, 11, 1).tolist()
counts3, bins = np.histogram(dist)
counts4, bins = np.histogram(distVent)

def wrap_labels(df, ax, width):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width, break_long_words=False))
    ax.set_xticklabels(df.columns, rotation=0, fontsize=8)
    ax.set_yticklabels(df.index, fontsize=8)

uno = round(counts1.sum()-counts1[0])
due = round(counts1.sum())
tre = round(counts3.sum()-counts3[0])
quattro = round(counts3.sum())
cinque = round(counts1.sum()-counts1[0]-counts1[1]-counts1[2])
sei = round(counts1.sum())
sette = round(counts3.sum()-counts3[0]-counts3[1]-counts3[2])
otto = round(counts3.sum())

unoVent = round(counts2.sum()-counts2[0])
dueVent = round(counts2.sum())
treVent = round(counts4.sum()-counts4[0])
quattroVent = round(counts4.sum())
cinqueVent = round(counts2.sum()-counts2[0]-counts2[1]-counts2[2])
seiVent = round(counts2.sum())
setteVent = round(counts4.sum()-counts4[0]-counts4[1]-counts4[2])
ottoVent = round(counts4.sum())

df_metrics = pd.DataFrame(columns = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], index = ["Velocità aria non aumentata", "Velocità aria aumentata"], data = [[uno, tre], [unoVent, treVent]])
df_metrics_tot = pd.DataFrame(columns = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], index = ["Velocità aria non aumentata", "Velocità aria aumentata"], data = [[due, quattro], [dueVent, quattroVent]])
  
df_metrics2 = pd.DataFrame(columns = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], index = ["Velocità aria non aumentata", "Velocità aria aumentata"], data = [[cinque, sette], [cinqueVent, setteVent]])
df_metrics_tot2 = pd.DataFrame(columns = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], index = ["Velocità aria non aumentata", "Velocità aria aumentata"], data = [[sei, otto], [seiVent, ottoVent]])

df_metrics = df_metrics.astype(float)
df_metrics_tot = df_metrics_tot.astype(float)
df_metrics2 = df_metrics2.astype(float)
df_metrics_tot2 = df_metrics_tot2.astype(float)

massimo = min((df_metrics/df_metrics_tot).values.max(), 0.30)

im = ax2.matshow(df_metrics/df_metrics_tot, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax2.set_xticks(np.arange(len(df_metrics.columns)), minor=False)
ax2.set_yticks(np.arange(len(df_metrics.index)), minor=False)
ax2.xaxis.tick_top()
ax2.grid(which="minor", c='black', ls=':', lw='0.4')
ax2.set_xticks([x-0.5 for x in range(1, len(df_metrics.columns))], minor=True)
ax2.set_yticks([y-0.5 for y in range(1, len(df_metrics.index))], minor=True)
wrap_labels(df_metrics, ax2, 5)

min_val, max_valRow = 0, 2
min_val, max_valCol = 0, 2

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df_metrics[df_metrics.columns[j]][df_metrics.index[k]]
        t = df_metrics_tot[df_metrics_tot.columns[j]][df_metrics_tot.index[k]]
        ax2.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=8)
         
ax2.text(0.5, -1.3, "N° di ore con T>Tmax / N° di ore totali", ha = "center", weight = "demi")

im = ax3.matshow(df_metrics2/df_metrics_tot2, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax3.set_xticks(np.arange(len(df_metrics2.columns)), minor=False)
ax3.set_yticks(np.arange(len(df_metrics2.index)), minor=False)
ax3.xaxis.tick_top()
ax3.grid(which="minor", c='black', ls=':', lw='0.4')
ax3.set_xticks([x-0.5 for x in range(1, len(df_metrics2.columns))], minor=True)
ax3.set_yticks([y-0.5 for y in range(1, len(df_metrics2.index))], minor=True)
wrap_labels(df_metrics2, ax3, 5)

min_val, max_valRow = 0, 2
min_val, max_valCol = 0, 2

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df_metrics2[df_metrics2.columns[j]][df_metrics2.index[k]]
        t = df_metrics_tot2[df_metrics_tot2.columns[j]][df_metrics_tot2.index[k]]
        ax3.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=8)
         
ax3.text(0.5, -1.3, "N° di ore con T>Tmax+2°C / N° di ore totali", ha = "center", weight = "demi")
st.pyplot(fig)

#%% Display results - TM52 compliance
st.write("Criteri di conformità con la norma TM52. Rischio di overheating in caso di fallimento di due o più criteri.")
st.markdown("- Criterio 1: \nla percentuale di ore con T > Tmax + 1°C deve essere ≤ 3% \n- Criterio 2: \nla percentuale di giorni con CDH > 6 gradi ore deve essere nulla (CDH - Gradi Ore di Raffrescamento = somma di T-Tmax per ogni ora) \n\n - Criterio 3: \nla percentule di ore con T > Tmax + 4°C deve essere nulla")
# st.write("TM52 regulations compliance: \nOverheating risk if failure of 2 or more criteria. \n\nCriterion 1: \nshare of hours with T > Tmax+1°C shall be ≤ 3% \n\nCriterion2: \nshare of days with CDH > 6 degree hours shall be null \nCDH (Cooling Degree Hours) = sum of T-Tmax at each hour \n\nCriterion 3: \nshare of hours with T > Tmax + 4°C shall be null") 

def numeri(max_valRow, max_valCol, df, ax):
    for j in range(max_valRow):
        for k in range(max_valCol):
            c = df[df.columns[j]][df.index[k]]
            ax.text(j, k, "{}%".format(str(round(c, 1))),
                     va='center', ha='center', fontsize=12)

def truefalse(max_valRow, max_valCol, df, ax):
    for j in range(max_valRow):
        for k in range(max_valCol):
            ax.text(j, k, "No overheating" if tot["TOT"].iloc[k] == 0 else "Overheating", va='center', ha='center', fontsize=8)
    
    
def wrap_labels2(df, ax, width):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width, break_long_words=False))
    ax.set_xticklabels(df.columns, rotation=0, fontsize=8)
    ax.set_yticklabels("", fontsize=8)
    
fig, (ax1,ax2) = plt.subplots(1,2)
fig.set_figheight(6)
fig.set_figwidth(9)

noVent = pd.concat([scenarios_df["C1"], scenarios_df["C2"], scenarios_df["C3"]], axis=1)
Vent = pd.concat([scenarios_df["C1_VENT"], scenarios_df["C2_VENT"], scenarios_df["C3_VENT"]], axis=1)
Vent.columns = ["C1", "C2", "C3"]
df = pd.concat([noVent, Vent])
df.index = ["Velocità aria non aumentata", "Velocità aria aumentata"]
df["TOT"] = 100
df.loc[(df["C1"] == 0) | (df["C2"] == 0) | (df["C3"] == 0), "TOT"] = 0

df = df.astype(float)

criteri = pd.concat([df["C1"], df["C2"], df["C3"]], axis=1)
im = ax1.matshow(criteri, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, 100])
ax1.set_xticks(np.arange(len(criteri.columns)), minor=False)
ax1.set_yticks(np.arange(len(criteri.index)), minor=False)
ax1.xaxis.tick_top()
ax1.grid(which="minor", c='black', ls=':', lw='0.4')
ax1.set_xticks([x-0.5 for x in range(1, len(criteri.columns))], minor=True)
ax1.set_yticks([y-0.5 for y in range(1, len(criteri.index))], minor=True)
wrap_labels(criteri, ax1, 5)

tot = pd.DataFrame(df["TOT"])
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

numeri(3, 2, criteri, ax1)
truefalse(1, 2, tot, ax2)

st.pyplot(fig)

# %% Display results - Heat wave adaptive chart
st.write("Giorni di stress termico elevato, calcolati come giorni in cui per almeno 3 giorni consecutivi la temperatura supera la Tmax, e in cui la ventilazione non può essere usata per abbassare la temperatura.")

# Days in which ventilation is feasible = days in which at ALL hours the temperature outside is lower than the indoor one and lower than the threshold
vent_df = pd.DataFrame(0, index=temp_df.index, columns=temp_df.columns)

vent_df.loc[(temp_df["Tout-{}".format(city)] < temp_df["Tmax-{}".format(city)] - 7)
            & (temp_df["Tout-{}".format(city)] < temp_df[caso]), caso] = 1

vent_daily = vent_df.resample("1440min").sum()
temp_daily = temp_df.resample("1440min").max()

heat_df = pd.DataFrame(0, index=temp_daily.index, columns=temp_daily.columns)
heat_df = heat_df.drop(columns=["Trm-{}".format(city), "Tmax-{}".format(
    city), "TmaxVent-{}".format(city), "Tout-{}".format(city)])
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

fig = plt.figure(figsize=(10, 6))

blue = sns.mpl_palette("Blues", 48)
red = sns.mpl_palette("Reds", 48)
green = sns.mpl_palette("Greens", 48)

plt.scatter(temp_daily["Trm-{}".format(city)],
            temp_daily[caso], color=blue[24], label="Giorni con T < Tmax")
plt.scatter(temp_daily["Trm-{}".format(city)][((temp_daily[caso] > temp_daily["Tmax-{}".format(city)]) | (temp_daily["Tout-{}".format(city)] > 30))],
            temp_daily[caso][((temp_daily[caso] > temp_daily["Tmax-{}".format(city)]) | (temp_daily["Tout-{}".format(city)] > 30))], color=red[12], label="Giorni con T > Tmax")
plt.scatter(temp_daily["Trm-{}".format(city)][((temp_daily[caso] > temp_daily["Tmax-{}".format(city)]) | (temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[caso] < 24)], temp_daily[caso]
            [((temp_daily[caso] > temp_daily["Tmax-{}".format(city)]) | (temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[caso] < 24)], color=red[24], label="Giorni con T > Tmax \nin cui la ventilazione \nnon è efficace")
plt.scatter(heat_df_updated["Trm"][heat_df_updated[caso] == 1], temp_daily[caso]
            [heat_df_updated[caso] == 1], color=red[36], label="Giorni di stress termico")

plt.plot((10, 30), (0.33 * 10 + 18.8 - 3, 0.33 * 30 + 18.8 - 3),
         color=green[12], label="Fascia I")
plt.plot((10, 30), (0.33 * 10 + 18.8 - 4, 0.33 * 30 + 18.8 - 4),
         color=green[24], label="Fascia II")
plt.plot((10, 30), (0.33 * 10 + 18.8 - 5, 0.33 * 30 + 18.8 - 5),
         color=green[36], label="Fascia III")
plt.plot((10, 30), (0.33 * 10 + 18.8 + 2,
         0.33 * 30 + 18.8 + 2), color=green[12])
plt.plot((10, 30), (0.33 * 10 + 18.8 + 3,
         0.33 * 30 + 18.8 + 3), color=green[24])
plt.plot((10, 30), (0.33 * 10 + 18.8 + 4,
         0.33 * 30 + 18.8 + 4), color=green[36])

xlimsinistra = min(min(temp_daily["Trm-{}".format(city)]), 10)
xlimdestra = max(max(temp_daily["Trm-{}".format(city)]), 30)
plt.xlim(xlimsinistra, xlimdestra)
plt.ylim(0, 45)
legend = plt.legend(loc="lower right", fontsize=10)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xlabel("Temperatura media mobile esterna [°C]", fontsize=15)
plt.ylabel("Temperatura operativa esterna [°C]", fontsize=15)

numeroTOT = round(heat_df_updated.sum(axis=0)[caso])
schoolNH_mask_daily = (heat_df_updated.index >= startNH) & (heat_df_updated.index < startSummer) | (heat_df_updated.index > endSummer) & (heat_df_updated.index < endNH)
heat_df_scuola = heat_df_updated.loc[schoolNH_mask_daily].copy()
numeroESTATE = round(heat_df_scuola.sum(axis=0)[caso])

plt.text((xlimdestra + xlimsinistra)/2, 46, "Numero di giorni di stress termico: {}, di cui {} durante il periodo scolastico".format(numeroTOT, numeroESTATE), ha = "center", fontsize = 12)

st.pyplot(fig)

# %% Possible retrofit
st.subheader("Confronto di soluzioni", divider = True)
st.write("Con il seguente elenco a scelta multipla è possibile comparare il potenziale di overheating di diverse configurazioni.")

if floor[0] == "T":
    if vent == "8 l/s/pers":
        if retrofit == "BASE":
            if valore == "alto":
                choices = ["Riduzione g-value", "Coibentazione pareti", "Coibentazione tetto",
                           "Serramenti doppi", "Aumentare la velocità dell'aria"]
            else:
                choices = ["Coibentazione pareti", "Coibentazione tetto",
                           "Serramenti doppi", "Aumentare la velocità dell'aria"]
        else:
            if valore == "alto":
                choices = ["Riduzione g-value",
                           "Aumentare la velocità dell'aria"]
            else:
                choices = ["Aumentare la velocità dell'aria"]
    else:
        if retrofit == "BASE":
            if valore == "alto":
                choices = ["Riduzione g-value", "Coibentazione pareti", "Coibentazione tetto",
                           "Serramenti doppi", "Aumentare la ventilazione", "Aumentare la velocità dell'aria"]
            else:
                choices = ["Coibentazione pareti", "Coibentazione tetto", "Serramenti doppi",
                           "Aumentare la ventilazione", "Aumentare la velocità dell'aria"]
        else:
            if valore == "alto":
                choices = ["Riduzione g-value",  "Aumentare la ventilazione",
                           "Aumentare la velocità dell'aria"]
            else:
                choices = ["Aumentare la ventilazione",
                           "Aumentare la velocità dell'aria"]
else:
    if vent == "8 l/s/pers":
        if retrofit == "BASE":
            if valore == "alto":
                choices = ["Riduzione g-value", "Coibentazione pareti",
                           "Serramenti doppi", "Aumentare la velocità dell'aria"]
            else:
                choices = ["Coibentazione pareti", "Serramenti doppi",
                           "Aumentare la velocità dell'aria"]
        else:
            if valore == "alto":
                choices = ["Riduzione g-value",
                           "Aumentare la velocità dell'aria"]
            else:
                choices = ["Aumentare la velocità dell'aria"]
    else:
        if retrofit == "BASE":
            if valore == "alto":
                choices = ["Riduzione g-value", "Coibentazione pareti", "Serramenti doppi",
                           "Aumentare la ventilazione", "Aumentare la velocità dell'aria"]
            else:
                choices = ["Coibentazione pareti", "Serramenti doppi",
                           "Aumentare la ventilazione", "Aumentare la velocità dell'aria"]
        else:
            if valore == "alto":
                choices = ["Riduzione g-value",  "Aumentare la ventilazione",
                           "Aumentare la velocità dell'aria"]
            else:
                choices = ["Aumentare la ventilazione",
                           "Aumentare la velocità dell'aria"]

inputsRetrofit = st.multiselect("Indicare le strategie di retrofit da comparare", choices, default=choices)
    
inputsRetrofit = [retrofit] + inputsRetrofit
number = len(inputsRetrofit)

if number == 1:
    diff = [0]
elif number == 2:
    diff = [-0.15, 0.15]
elif number == 3:
    diff = [-0.2, 0, 0.2]
elif number == 4:
    diff = [-0.3, -0.1, 0.1, 0.3]
elif number == 5:
    diff = [-0.3, -0.15, 0, 0.15, 0.3]
elif number == 6:
    diff = [-0.3, -0.18, -0.06, 0.06, 0.18, 0.3]
elif number == 7:
    diff = [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3]
    
    
st.write("Nei prossimi grafici verranno usate le seguenti etichette:")

for element in inputsRetrofit:
    if element == "Coibentazione pareti":
        testo = "WALL = Coibentazione pareti"
    elif element == "Coibentazione tetto":
        testo = "ROOF = Coibentazione tetto"
    elif element == "Serramenti doppi":
        testo = "WINDOW = Serramenti doppi"
    elif element == "Aumentare la ventilazione":
        testo = "8 l/s/pers = Aumentare la ventilazione"
    elif element == "Aumentare la velocità dell'aria":
        testo = "1.2 m/s = Aumentare la velocità dell'aria"
    elif element == "Riduzione g-value":
        testo = "G-VALUE = Riduzione g-value"
    elif element == "BASE":
        testo = "BASE = Configurazione iniziale"
    elif element == "WALL":
        testo = "WALL = Configurazione iniziale - Coibentazione pareti"
    elif element == "ROOF":
        testo = "ROOF = Configurazione iniziale - Coibentazione tetto"
    elif element == "WALL":
        testo = "WINDOW = Configurazione iniziale - Serramenti doppi"
    
    st.markdown("- {}".format(testo))

# Create new dataframe for comparison
temp_df_compare = temp_df.copy()
temp_df_compare["BASE"] = temp_df[caso]
dist_df_compare = dist_df_tot[dist_df_tot["Unnamed: 0"] == "bins"]
scenarios_df_compare = pd.DataFrame(columns=scenarios_df.columns)

for element in inputsRetrofit:
    if element == "Riduzione g-value":
        SHGC_new = 0.3
        retrofit_new = retrofit
        vent_new = vent
    else:
        SHGC_new = SHGC
        if element == "Coibentazione pareti":
            retrofit_new = "WALL"
        elif element == "Coibentazione tetto":
            retrofit_new = "ROOF"
        elif element == "Serramenti doppi":
            retrofit_new = "WINDOW"
        else:
            retrofit_new = retrofit
        if element == "Aumentare la ventilazione":
            vent_new = "8 l/s/pers"
        else:
            vent_new = vent

    if element != "Aumentare la velocità dell'aria":
        if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in temp_df_tot:
            caso_elem = "-{}, {}, {}, {}, {}, {}, {}".format(
                city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
        elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in temp_df_tot:
            caso_elem = "-{}, {}, {}, {}, {}, {}.0, {}".format(
                city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
        elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in temp_df_tot:
            caso_elem = "-{}, {}, {}, {}, {}.0, {}, {}".format(
                city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
        elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in temp_df_tot:
            caso_elem = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(
                city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)

        if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in dist_df_tot["Unnamed: 0"].values:
            casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(
                city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
        elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in dist_df_tot["Unnamed: 0"].values:
            casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(
                city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
        elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in dist_df_tot["Unnamed: 0"].values:
            casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(
                city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
        elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in dist_df_tot["Unnamed: 0"].values:
            casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(
                city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)

        temp_df_compare[element] = temp_df_tot[caso_elem]
        dist_df_compare = pd.concat([dist_df_compare, dist_df_tot[dist_df_tot["Unnamed: 0"]
                                    == casoDist], dist_df_tot[dist_df_tot["Unnamed: 0"] == "{} VENT".format(casoDist)]])
        scenarios_df_compare = pd.concat([scenarios_df_compare, scenarios_df_tot[(scenarios_df_tot["window_to_floor_ratio"] == WFR/100) & (scenarios_df_tot["building_orientation"] == orient) & (
            scenarios_df_tot["solar_heat_gain_coefficient"] == SHGC_new) & (scenarios_df_tot["THERMAL"] == retrofit_new) & (scenarios_df_tot["VENT"] == vent_new)]])

# %% Display results - comfort bands
st.write("Percentuale di ore nelle categorie di comfort suddivise per periodi sulla base dell'accensione del riscaldamento e sulle vacanze estive. Confronto tra diverse soluzioni.")
plt.rcParams.update({'font.size': 10})
periodCase = pd.DataFrame(index=[0, 1, 2, 3, 4], columns=["C1", "C2", "C3", "Overheating", "C1_VENT", "C2_VENT", "C3_VENT", "Overheating_VENT", "low", "lowBand3",
                          "lowBand2", "Band1", "highBand2", "highBand3", "high", "lowVent", "lowBand3Vent", "lowBand2Vent", "Band1Vent", "highBand2Vent", "highBand3Vent", "highVent"])

startSummer = "2025-06-15 00:00:00"
endSummer = "2025-09-15 00:00:00"

P1_mask = (temp_df.index >= "2025-01-01 00:00:00") & (temp_df.index < startNH)
P2_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer)
P3_mask = (temp_df.index >= startSummer) & (temp_df.index < endSummer)
P4_mask = (temp_df.index >= endSummer) & (temp_df.index < endNH)
P5_mask = (temp_df.index >= endNH) & (temp_df.index <= "2025-12-31 23:00:00")

fig, ax = plt.subplots()
fig.set_figheight(6)
fig.set_figwidth(9)
w = 0.5

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    if (comparazione == "BASE") | (comparazione == "WALL") | (comparazione == "ROOF") | (comparazione == "WINDOW"):
        iniziale = comparazione
    elif comparazione == "Riduzione g-value":
        iniziale = "G-VALUE"
    elif comparazione == "Coibentazione pareti":
        iniziale = "WALL"
    elif comparazione == "Coibentazione tetto":
        iniziale = "ROOF"
    elif comparazione == "Serramenti doppi":
        iniziale = "WINDOW"
    elif comparazione == "Aumentare la ventilazione":
        iniziale = "8 l/s/pers"
    elif comparazione == "Aumentare la velocità dell'aria":
        comparazione = "BASE"
        iniziale = "1.2 m/s"

    temp_comparazione = pd.concat(
        [temp_df_compare[comparazione], temp_df_compare["Tout-{}".format(city)]], axis=1)

    temp_df_P1 = temp_comparazione.loc[P1_mask].copy()
    temp_df_P2 = temp_comparazione.loc[P2_mask].copy()
    temp_df_P3 = temp_comparazione.loc[P3_mask].copy()
    temp_df_P4 = temp_comparazione.loc[P4_mask].copy()
    temp_df_P5 = temp_comparazione.loc[P5_mask].copy()

    temp_list = [temp_df_P1, temp_df_P2, temp_df_P3, temp_df_P4, temp_df_P5]
    nomi = ["Inizio dell'anno - \nspegnimento \nriscaldamento", "Spegnimento \nriscaldamento - \nfine della scuola",
            "Fine - inizio \ndella scuola", "Inizio della scuola - \naccensione \nriscaldamento", "Accensione \nriscaldamento - \nfine dell'anno"]

    for periodo in [0, 1, 2, 3, 4]:
        nomePeriodo = nomi[periodo]
        temp_period = temp_list[periodo]

        temp_period_case = temp_period[comparazione]
        temp_out_period = temp_period["Tout-{}".format(city)].values

        temp, Trm, Tmax, percentC1, percentC2, percentC3, overheating, Tmax_vent, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, dist_df_period, low, lowBand3, lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent = exceeding_hours_TM52(
            temp_out_period, temp_period_case, climatic_zone)

        # Save results
        lista = [percentC1, percentC2, percentC3, overheating, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, low, lowBand3,
                 lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent]
        periodCase.loc[periodo] = lista

    if inputsRetrofit[comparazione_numero] == "Aumentare la velocità dell'aria":
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 +
               diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["lowVent"], w/number, color="#90e0ef", label="T<Tmin")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 +
               diff[comparazione_numero]], periodCase["lowBand3Vent"],  w/number, bottom=periodCase["lowVent"], color="#ddead1", label="III fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["lowBand2Vent"],  w/number, bottom=periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#95bb72", label="II fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["Band1Vent"],  w/number, bottom=periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#4b6043", label="I fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["highBand2Vent"],  w/number, bottom=periodCase["Band1Vent"] + periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#95bb72")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["highBand3Vent"],
               w/number, bottom=periodCase["highBand2Vent"] + periodCase["Band1Vent"] + periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#ddead1")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["highVent"],  w/number,
               bottom=periodCase["highBand3Vent"] + periodCase["highBand2Vent"] + periodCase["Band1Vent"] + periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#f69697", label="T>Tmax")

    else:
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 +
               diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["low"], w/number, color="#90e0ef", label="T<Tmin")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 +
               diff[comparazione_numero]], periodCase["lowBand3"],  w/number, bottom=periodCase["low"], color="#ddead1", label="III fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 +
               diff[comparazione_numero]], periodCase["lowBand2"],  w/number, bottom=periodCase["lowBand3"] + periodCase["low"], color="#95bb72", label="II fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["Band1"],  w/number, bottom=periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#4b6043", label="I fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["highBand2"],  w/number, bottom=periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#95bb72")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["highBand3"],  w/number, bottom=periodCase["highBand2"] + periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#ddead1")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["high"],  w /
               number, bottom=periodCase["highBand3"] + periodCase["highBand2"] + periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#f69697", label="T>Tmax")
    handles, labels = ax.get_legend_handles_labels()

    ax.text(0 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(1 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(2 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(3 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(4 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)

ax.set_xticks([0, 1, 2, 3, 4], nomi)
ax.text(xgen, ypisl, "GEN", color=sns.mpl_palette("Set2")[2], ha="center")
ax.text(xfeb, ypisl, "FEB", color=sns.mpl_palette("Set2")[2], ha="center")
ax.text(xmar, ypisl, "MAR", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xapr, ypisl, "APR", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xmay, ypisl, "MAG", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xjun, ypisl, "GIU", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xjul, ypisl, "LUG", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xaug, ypisl, "AGO", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xsep, ypisl, "SET", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xoct, ypisl, "OTT", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xnov, ypisl, "NOV", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xdec, ypisl, "DIC", color=sns.mpl_palette("Set2")[2], ha="center")

ax.set_ylim(0, 100)
ax.text(-1, 50, "Percentuale di ore in ciascuna fascia di comfort [%]", rotation="vertical", va="center")

fig.legend(handles[:5], labels[:5], loc='upper center', ncol=7)

st.pyplot(fig)

# %% Display results - temperature distribution
st.write("Distribuzione di frequenza delle temperature sopra alla Tmax. Dati riferiti al periodo di spegnimento del riscaldamento. Confronto tra diverse soluzioni.")

plt.rcParams.update({'font.size': 7})

fig, axs = plt.subplot_mosaic([['dist', 'scritte1'], ['dist', 'scritte2']], layout='constrained')
ax1 = axs["dist"]
ax2 = axs["scritte1"]
ax3 = axs["scritte2"]

fig.set_figheight(6)
fig.set_figwidth(9)

df_label = pd.DataFrame(index = ["Label"])
df_metrics = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)
df_metrics_tot = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)
df_metrics2 = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)
df_metrics_tot2 = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    if (comparazione == "BASE") | (comparazione == "WALL") | (comparazione == "ROOF") | (comparazione == "WINDOW"):
        iniziale = comparazione
    elif comparazione == "Riduzione g-value":
        iniziale = "G-VALUE"
    elif comparazione == "Coibentazione pareti":
        iniziale = "WALL"
    elif comparazione == "Coibentazione tetto":
        iniziale = "ROOF"
    elif comparazione == "Serramenti doppi":
        iniziale = "WINDOW"
    elif comparazione == "Aumentare la ventilazione":
        iniziale = "8 l/s/pers"
    elif comparazione == "Aumentare la velocità dell'aria":
        iniziale = "1.2 m/s"

    if comparazione == "Riduzione g-value":
        SHGC_new = 0.3
        retrofit_new = retrofit
        vent_new = vent
    else:
        SHGC_new = SHGC
        if comparazione == "Coibentazione pareti":
            retrofit_new = "WALL"
        elif comparazione == "Coibentazione tetto":
            retrofit_new = "ROOF"
        elif comparazione == "Serramenti doppi":
            retrofit_new = "WINDOW"
        else:
            retrofit_new = retrofit
        if comparazione == "Aumentare la ventilazione":
            vent_new = "8 l/s/pers"
        else:
            vent_new = vent

    if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in dist_df_tot["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
    elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in dist_df_tot["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
    elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in dist_df_tot["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
    elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new) in dist_df_tot["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent_new, retrofit_new, WFR, orient, SHGC_new)
    
    
    if comparazione == "Aumentare la velocità dell'aria":
        temp_df = pd.concat([temp_df_compare["BASE"], temp_df_compare["Month"], temp_df_compare["Weekday"], temp_df_compare["Hour"],  temp_df_compare["Tmax-{}".format(city)],  temp_df_compare["TmaxVent-{}".format(city)]], axis = 1)
        temp_df["Occupied"] = (temp_df["Month"].isin(occupied_months) & temp_df["Weekday"].isin(occupied_weekdays) & temp_df["Hour"].isin(occupied_hours))

        ax1.plot(dist_df_compare[dist_df_compare["Unnamed: 0"] == "bins"].drop(columns=["Unnamed: 0"]).values.flatten(), dist_df_compare[dist_df_compare["Unnamed: 0"] == "{} VENT".format(casoDist)].drop(columns=["Unnamed: 0"]).values.flatten()*100, label="Increased air speed".format(iniziale), color=blue[round(48/number*comparazione_numero)])
        
        # ALl non heating period
        nonheat_mask = (temp_df.index >= startNH) & (temp_df.index < endNH)
        df_nonheat = temp_df.loc[nonheat_mask].copy()
        df_occ = df_nonheat[df_nonheat["Occupied"]].copy()
        dist = np.where(df_occ["BASE"] > df_occ["TmaxVent-{}".format(city)],df_occ["BASE"] - df_occ["TmaxVent-{}".format(city)], 0)
        bins = np.arange(0, 11, 1).tolist()
        counts1, bins = np.histogram(dist)
        
        # School non heating period
        schoolNH_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer) | (temp_df.index > endSummer) & (temp_df.index < endNH)
        df_schoolNH = temp_df.loc[schoolNH_mask].copy()
        df_occ = df_schoolNH[df_schoolNH["Occupied"]].copy()
        dist = np.where(df_occ["BASE"] > df_occ["TmaxVent-{}".format(city)],df_occ["BASE"] - df_occ["TmaxVent-{}".format(city)], 0)
        bins = np.arange(0, 11, 1).tolist()
        counts3, bins = np.histogram(dist)

    else:
        temp_df = pd.concat([temp_df_compare[comparazione], temp_df_compare["Month"], temp_df_compare["Weekday"], temp_df_compare["Hour"],  temp_df_compare["Tmax-{}".format(city)],  temp_df_compare["TmaxVent-{}".format(city)]], axis = 1)
        temp_df["Occupied"] = (temp_df["Month"].isin(occupied_months) & temp_df["Weekday"].isin(occupied_weekdays) & temp_df["Hour"].isin(occupied_hours))

        ax1.plot(dist_df_compare[dist_df_compare["Unnamed: 0"] == "bins"].drop(columns=["Unnamed: 0"]).values.flatten(), dist_df_compare[dist_df_compare["Unnamed: 0"] == casoDist].drop(columns=["Unnamed: 0"]).values.flatten()*100, label=iniziale, color=red[round(48/number*comparazione_numero)])
        
        # ALl non heating period
        nonheat_mask = (temp_df.index >= startNH) & (temp_df.index < endNH)
        df_nonheat = temp_df.loc[nonheat_mask].copy()
        df_occ = df_nonheat[df_nonheat["Occupied"]].copy()
        dist = np.where(df_occ[comparazione] > df_occ["Tmax-{}".format(city)],df_occ[comparazione] - df_occ["Tmax-{}".format(city)], 0)
        bins = np.arange(0, 11, 1).tolist()
        counts1, bins = np.histogram(dist)

        # School non heating period
        schoolNH_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer) | (temp_df.index > endSummer) & (temp_df.index < endNH)
        df_schoolNH = temp_df.loc[schoolNH_mask].copy()
        df_occ = df_schoolNH[df_schoolNH["Occupied"]].copy()
        dist = np.where(df_occ[comparazione] > df_occ["Tmax-{}".format(city)],df_occ[comparazione] - df_occ["Tmax-{}".format(city)], 0)
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
    
    df_label[comparazione] = iniziale
    df_metrics[comparazione] = [uno, tre]
    df_metrics_tot[comparazione] = [due, quattro]
    df_metrics2[comparazione] = [cinque, sette]
    df_metrics_tot2[comparazione] = [sei, otto]
    
    df_metrics = df_metrics.astype(float)
    df_metrics_tot = df_metrics_tot.astype(float)
    df_metrics2 = df_metrics2.astype(float)
    df_metrics_tot2 = df_metrics_tot2.astype(float)

    ax1.xaxis.set_tick_params(labelbottom=True)
    ax1.yaxis.set_tick_params(labelbottom=True)
    ax1.set_ylim(0, 100)
    ax1.set_xlim(0, 9)
    ax1.set_xticks(range(0, 10))

    ax1.set_xlabel("T - Tmax [°C]", ha='center')
    ax1.set_ylabel("Frequenza cumulata [%]", va='center', rotation='vertical')

df_label = df_label.transpose()
df_metrics = df_metrics.transpose()
df_metrics_tot = df_metrics_tot.transpose()
df_metrics2 = df_metrics2.transpose()
df_metrics_tot2 = df_metrics_tot2.transpose()

df_metrics = df_metrics.set_index(df_label["Label"])
df_metrics_tot = df_metrics_tot.set_index(df_label["Label"])
df_metrics2 = df_metrics2.set_index(df_label["Label"])
df_metrics_tot2 = df_metrics_tot2.set_index(df_label["Label"])

ax1.text(4.5, 103, "PERIODO NON RISCALDATO, ORE OCCUPATE", ha = "center", weight = "demi")    
ax1.axvspan(2, 9, alpha = 0.3, color = red[24], label = "Estremamente inaccettabile")
ax1.axhspan(0, 95, xmin = 0, xmax = 2/9, alpha = 0.3, color = red[12], label = "Inaccettabile")
ax1.axhspan(95, 100, xmin = 0, xmax = 2/9, alpha = 0.3, color=green[24], label = "Trascurabilmente inaccettabile")

if number >= 4:
    fig.legend(bbox_to_anchor=[0.5, 1.17], ncol=2, fontsize=10)
else:
    fig.legend(bbox_to_anchor=[0.5, 1.07], ncol=2, fontsize=10)

def wrap_labels3(df, ax, width):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width, break_long_words=False))
    ax.set_xticklabels(df.columns, rotation=0, fontsize=8) #df_label.loc["Label"]
    ax.set_yticklabels(df.index, fontsize=10)
    
im = ax2.matshow(df_metrics/df_metrics_tot, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax2.set_xticks(np.arange(len(df_metrics.columns)), minor=False)
ax2.set_yticks(np.arange(len(df_metrics.index)), minor=False)
ax2.xaxis.tick_top()
ax2.grid(which="minor", c='black', ls=':', lw='0.4')
ax2.set_xticks([x-0.5 for x in range(1, len(df_metrics.columns))], minor=True)
ax2.set_yticks([y-0.5 for y in range(1, len(df_metrics.index))], minor=True)
wrap_labels3(df_metrics, ax2, 5)

min_val, max_valRow = 0, 2
min_val, max_valCol = 0, number

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df_metrics[df_metrics.columns[j]][df_metrics.index[k]]
        t = df_metrics_tot[df_metrics_tot.columns[j]][df_metrics_tot.index[k]]
        ax2.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=8)
         
ax2.text(0.5, -1.3, "N° di ore con T>Tmax / N° di ore totali", ha = "center", weight = "demi")

im = ax3.matshow(df_metrics2/df_metrics_tot2, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax3.set_xticks(np.arange(len(df_metrics2.columns)), minor=False)
ax3.set_yticks(np.arange(len(df_metrics2.index)), minor=False)
ax3.xaxis.tick_top()
ax3.grid(which="minor", c='black', ls=':', lw='0.4')
ax3.set_xticks([x-0.5 for x in range(1, len(df_metrics2.columns))], minor=True)
ax3.set_yticks([y-0.5 for y in range(1, len(df_metrics2.index))], minor=True)
wrap_labels3(df_metrics2, ax3, 5)

min_val, max_valRow = 0, 2
min_val, max_valCol = 0, number

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df_metrics[df_metrics2.columns[j]][df_metrics2.index[k]]
        t = df_metrics_tot[df_metrics_tot2.columns[j]][df_metrics_tot2.index[k]]
        ax3.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=8)
         
ax3.text(0.5, -1.3, "N° di ore con T>Tmax+2°C / N° di ore totali", ha = "center", weight = "demi")
st.pyplot(fig)

#%% Display results - TM52 compliance
st.write("Criteri di conformità con la norma TM52. Confronto tra diverse soluzioni.")

fig, (ax1,ax2) = plt.subplots(1,2)
fig.set_figheight(6)
fig.set_figwidth(9)

Vent = pd.DataFrame(columns=["C1", "C2", "C3"])
noVent = pd.DataFrame(columns=["C1", "C2", "C3"])

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    if (comparazione == "BASE") | (comparazione == "WALL") | (comparazione == "ROOF") | (comparazione == "WINDOW"):
        iniziale = comparazione
    elif comparazione == "Riduzione g-value":
        iniziale = "G-VALUE"
    elif comparazione == "Coibentazione pareti":
        iniziale = "WALL"
    elif comparazione == "Coibentazione tetto":
        iniziale = "ROOF"
    elif comparazione == "Serramenti doppi":
        iniziale = "WINDOW"
    elif comparazione == "Aumentare la ventilazione":
        iniziale = "8 l/s/pers"
    elif comparazione == "Aumentare la velocità dell'aria":
        iniziale = "1.2 m/s"

    if comparazione == "Riduzione g-value":
        SHGC_new = 0.3
        retrofit_new = retrofit
        vent_new = vent
    else:
        SHGC_new = SHGC
        if comparazione == "Coibentazione pareti":
            retrofit_new = "WALL"
        elif comparazione == "Coibentazione tetto":
            retrofit_new = "ROOF"
        elif comparazione == "Serramenti doppi":
            retrofit_new = "WINDOW"
        else:
            retrofit_new = retrofit
        if comparazione == "Aumentare la ventilazione":
            vent_new = "8 l/s/pers"
        else:
            vent_new = vent

    if comparazione == "Aumentare la velocità dell'aria":
        Vent.loc[iniziale, "C1"] = float(scenarios_df_compare["C1_VENT"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (
            scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)].values[0])
        Vent.loc[iniziale, "C2"] = float(scenarios_df_compare["C2_VENT"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (
            scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)].values[0])
        Vent.loc[iniziale, "C3"] = float(scenarios_df_compare["C3_VENT"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (
            scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)].values[0])
    else:
        noVent.loc[iniziale, "C1"] = float(scenarios_df_compare["C1"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (
            scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)].values[0])
        noVent.loc[iniziale, "C2"] = float(scenarios_df_compare["C2"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (
            scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)].values[0])
        noVent.loc[iniziale, "C3"] = float(scenarios_df_compare["C3"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (
            scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)].values[0])

    df = pd.concat([noVent, Vent])
    # df.index = ["Zero air speed", "Increased air speed"]
    df["TOT"] = 100
    df.loc[(df["C1"] == 0) | (df["C2"] == 0) | (df["C3"] == 0), "TOT"] = 0
    df = df.astype('float64')

criteri = pd.concat([df["C1"], df["C2"], df["C3"]], axis=1)
im = ax1.matshow(criteri, cmap="RdYlGn_r",interpolation="none", aspect = 0.5)
im.norm.autoscale([0, 100])
ax1.set_xticks(np.arange(len(criteri.columns)), minor=False)
ax1.set_yticks(np.arange(len(criteri.index)), minor=False)
ax1.xaxis.tick_top()
ax1.grid(which="minor", c='black', ls=':', lw='0.4')
ax1.set_xticks([x-0.5 for x in range(1, len(criteri.columns))], minor=True)
ax1.set_yticks([y-0.5 for y in range(1, len(criteri.index))], minor=True)
wrap_labels(criteri, ax1, 5)

min_val, max_valRow = 0, 3
min_val, max_valCol = 0, number

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df[criteri.columns[j]][criteri.index[k]]
        ax1.text(j, k, "{}%".format(str(round(c, 1))), va='center', ha='center', fontsize=10)

tot = pd.DataFrame(df["TOT"])
tot = tot.astype(float)    
im = ax2.matshow(tot, cmap="RdYlGn_r", interpolation="none", aspect = 0.5/3)
im.norm.autoscale([0, 100])
ax2.set_xticks(np.arange(len(tot.columns)), minor=False)
ax2.set_yticks(np.arange(len(tot.index)), minor=False)
ax2.xaxis.tick_top()
ax2.grid(which="minor", c='black', ls=':', lw='0.4')
ax2.set_xticks([x-0.5 for x in range(1, len(tot.columns))], minor=True)
ax2.set_yticks([y-0.5 for y in range(1, len(tot.index))], minor=True)
wrap_labels2(tot, ax2, 5)

truefalse(1, number, tot, ax2)

st.pyplot(fig)

# %% Calculate share of overheating days
heat_stress = pd.DataFrame(columns = ["Giorni di stress termico totali", "Giorni di stress termico periodo scolastico non riscaldato"], index = range(number))
heat_stress_tot = pd.DataFrame(columns = ["total", "school non heating"], index = range(number))
indice = pd.DataFrame(columns = ["caso"], index = range(number))

scenarios_df_compare["Overheating days share"] = ""
scenarios_df_compare["Overheating days share with increased air speed"] = ""

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    if (comparazione == "BASE") | (comparazione == "WALL") | (comparazione == "ROOF") | (comparazione == "WINDOW"):
        iniziale = comparazione
    elif comparazione == "Riduzione g-value":
        iniziale = "G-VALUE"
    elif comparazione == "Coibentazione pareti":
        iniziale = "WALL"
    elif comparazione == "Coibentazione tetto":
        iniziale = "ROOF"
    elif comparazione == "Serramenti doppi":
        iniziale = "WINDOW"
    elif comparazione == "Aumentare la ventilazione":
        iniziale = "8 l/s/pers"
    elif comparazione == "Aumentare la velocità dell'aria":
        iniziale = "1.2 m/s"

    if comparazione == "Riduzione g-value":
        SHGC_new = 0.3
        retrofit_new = retrofit
        vent_new = vent
    else:
        SHGC_new = SHGC
        if comparazione == "Coibentazione pareti":
            retrofit_new = "WALL"
        elif comparazione == "Coibentazione tetto":
            retrofit_new = "ROOF"
        elif comparazione == "Serramenti doppi":
            retrofit_new = "WINDOW"
        else:
            retrofit_new = retrofit
        if comparazione == "Aumentare la ventilazione":
            vent_new = "8 l/s/pers"
        else:
            vent_new = vent

    if comparazione != "Aumentare la velocità dell'aria":
        temp_comparazione = pd.concat([temp_df_compare[comparazione], temp_df_compare["Tout-{}".format(city)], temp_df_compare["Tmax-{}".format(
            city)], temp_df_compare["TmaxVent-{}".format(city)], temp_df_compare["Trm-{}".format(city)]], axis=1)

        # Days in which ventilation is feasible = days in which at ALL hours the temperature outside is lower than the indoor one and lower than the threshold
        vent_comparazione = pd.DataFrame(
            0, index=temp_comparazione.index, columns=temp_comparazione.columns)

        vent_comparazione.loc[(temp_comparazione["Tout-{}".format(city)] < temp_comparazione["Tmax-{}".format(city)] - 7)
                              & (temp_comparazione["Tout-{}".format(city)] < temp_comparazione[comparazione]), comparazione] = 1

        vent_daily = vent_comparazione.resample("1440min").sum()
        temp_daily = temp_comparazione.resample("1440min").max()

        heat_comparazione = pd.DataFrame(
            0, index=temp_daily.index, columns=temp_daily.columns)
        heat_comparazione = heat_comparazione.drop(columns=["Tmax-{}".format(
            city), "TmaxVent-{}".format(city), "Tout-{}".format(city), "Trm-{}".format(city)])

        # Share of days in which indoor temperature is above the threshold and ventilation is not feasible, or in which Trm is above 30°C (limit of the adaptive chart)
        heat_comparazione.loc[((temp_daily[comparazione] > temp_daily["Tmax-{}".format(city)]) | (
            temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[comparazione] < 24), comparazione] = 1

        share = heat_comparazione.sum(axis=0) / 365 * 100

        # At least 3 consecutive days to be considered heat wave
        heat_comparazione_updated = heat_comparazione.copy()

        for day in heat_comparazione.index:
            if (day == pd.Timestamp('2025-01-01 00:00:00')) | (day == pd.Timestamp('2025-01-02 00:00:00')) | (day == pd.Timestamp('2025-12-30 00:00:00')) | (day == pd.Timestamp('2025-12-31 00:00:00')):
                ieri = 0
                laltroieri = 0
                oggi = heat_comparazione[comparazione][day]
                domani = 0
                dopodomani = 0
            else:
                laltroieri = heat_comparazione[comparazione][day -
                                                             pd.to_timedelta(2, unit='D')]
                ieri = heat_comparazione[comparazione][day -
                                                       pd.to_timedelta(1, unit='D')]
                oggi = heat_comparazione[comparazione][day]
                domani = heat_comparazione[comparazione][day +
                                                         pd.to_timedelta(1, unit='D')]
                dopodomani = heat_comparazione[comparazione][day +
                                                             pd.to_timedelta(2, unit='D')]

            if oggi == 1:
                if ((domani == 1) & (dopodomani == 1)) | ((ieri == 1) & (laltroieri == 1)) | ((ieri == 1) & (domani == 1)):
                    heat_comparazione_updated.loc[day, comparazione] = 1
                else:
                    heat_comparazione_updated.loc[day, comparazione] = 0

        share_updated = float(
            heat_comparazione_updated.sum(axis=0).values[0]) / 365 * 100
        # scenarios_df_compare["Overheating days share"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)] = float(heat_comparazione_updated.sum(axis = 0).values) / 365 * 100
        
        numeroTOT = round(heat_comparazione_updated.sum(axis=0)[comparazione])
        schoolNH_mask_daily = (heat_comparazione_updated.index >= startNH) & (heat_comparazione_updated.index < startSummer) | (heat_comparazione_updated.index > endSummer) & (heat_comparazione_updated.index < endNH)
        heat_comparazione_scuola = heat_comparazione_updated.loc[schoolNH_mask_daily].copy()
        numeroESTATE = round(heat_comparazione_scuola.sum(axis=0)[comparazione])
        
    else:
        comparazione = "BASE"
        temp_comparazione = pd.concat([temp_df_compare[comparazione], temp_df_compare["Tout-{}".format(city)], temp_df_compare["Tmax-{}".format(
            city)], temp_df_compare["TmaxVent-{}".format(city)], temp_df_compare["Trm-{}".format(city)]], axis=1)

        # Days in which ventilation is feasible = days in which at ALL hours the temperature outside is lower than the indoor one and lower than the threshold
        vent_comparazione = pd.DataFrame(
            0, index=temp_comparazione.index, columns=temp_comparazione.columns)

        vent_comparazione.loc[(temp_comparazione["Tout-{}".format(city)] < temp_comparazione["Tmax-{}".format(city)] - 7)
                              & (temp_comparazione["Tout-{}".format(city)] < temp_comparazione[comparazione]), comparazione] = 1

        vent_daily = vent_comparazione.resample("1440min").sum()
        temp_daily = temp_comparazione.resample("1440min").max()

        heat_comparazione = pd.DataFrame(
            0, index=temp_daily.index, columns=temp_daily.columns)
        heat_comparazione = heat_comparazione.drop(columns=["Tmax-{}".format(
            city), "TmaxVent-{}".format(city), "Tout-{}".format(city), "Trm-{}".format(city)])
        heat_comparazione_vent = heat_comparazione.copy()

        # Share of days in which indoor temperature is above the threshold and ventilation is not feasible, or in which Trm is above 30°C (limit of the adaptive chart)
        heat_comparazione_vent.loc[((temp_daily[comparazione] > temp_daily["TmaxVent-{}".format(city)]) | (
            temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[comparazione] < 24), comparazione] = 1

        share = heat_comparazione.sum(axis=0) / 365 * 100

        # At least 3 consecutive days to be considered heat wave
        heat_comparazione_vent_updated = heat_comparazione_vent.copy()

        for day in heat_comparazione_vent.index:
            if (day == pd.Timestamp('2025-01-01 00:00:00')) | (day == pd.Timestamp('2025-01-02 00:00:00')) | (day == pd.Timestamp('2025-12-30 00:00:00')) | (day == pd.Timestamp('2025-12-31 00:00:00')):
                ieri = 0
                laltroieri = 0
                oggi = heat_comparazione_vent[comparazione][day]
                domani = 0
                dopodomani = 0
            else:
                laltroieri = heat_comparazione_vent[comparazione][day -
                                                                  pd.to_timedelta(2, unit='D')]
                ieri = heat_comparazione_vent[comparazione][day -
                                                            pd.to_timedelta(1, unit='D')]
                oggi = heat_comparazione_vent[comparazione][day]
                domani = heat_comparazione_vent[comparazione][day +
                                                              pd.to_timedelta(1, unit='D')]
                dopodomani = heat_comparazione_vent[comparazione][day +
                                                                  pd.to_timedelta(2, unit='D')]

            if oggi == 1:
                if ((domani == 1) & (dopodomani == 1)) | ((ieri == 1) & (laltroieri == 1)) | ((ieri == 1) & (domani == 1)):
                    heat_comparazione_vent_updated.loc[day, comparazione] = 1
                else:
                    heat_comparazione_vent_updated.loc[day, comparazione] = 0

        share_updated = float(
            heat_comparazione_vent_updated.sum(axis=0).values[0]) / 365 * 100
        # scenarios_df_compare["Overheating days share with increased air speed"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)] = float(heat_comparazione_vent_updated.sum(axis = 0).values) / 365 * 100
        
        numeroTOT = round(heat_comparazione_vent_updated.sum(axis=0)[comparazione])
        schoolNH_mask_daily = (heat_comparazione_vent_updated.index >= startNH) & (heat_comparazione_vent_updated.index < startSummer) | (heat_comparazione_updated.index > endSummer) & (heat_comparazione_updated.index < endNH)
        heat_comparazione_vent_scuola = heat_comparazione_vent_updated.loc[schoolNH_mask_daily].copy()
        numeroESTATE = round(heat_comparazione_vent_scuola.sum(axis=0)[comparazione])
    
    indice.loc[comparazione_numero] = [iniziale]        
    heat_stress.loc[comparazione_numero] = [numeroTOT, numeroESTATE]
    heat_stress = heat_stress.astype(float)
    heat_stress_tot.loc[comparazione_numero] = [365, heat_df_scuola.shape[0]]
    
heat_stress = heat_stress.set_index(indice["caso"])
heat_stress_tot = heat_stress_tot.set_index(indice["caso"])

st.write("Giorni totali di stress termico e giorni di stress termico per il periodo scolastico di spegnimento del riscaldamento. Confronto tra diverse soluzioni.")
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

def numeri2(max_valRow, max_valCol, df, dftot, ax):
    for j in range(max_valRow):
        for k in range(max_valCol):
            c = df[df.columns[j]][df.index[k]]
            t = dftot[dftot.columns[j]][dftot.index[k]]
            ax.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=12)

numeri2(2, number, heat_stress, heat_stress_tot, ax)

st.pyplot(fig)

#%% Additional passive strategies

# If we are dealing with a corner position --> no results --> change to middle
if floor.split("-")[1] == "C":
    st.write("Per le classi in posizione angolare sono state effettuate simulazioni solo del caso base. Per comparare strategie passive selezionare la classe con un solo affaccio.")
    st.stop()
    
st.subheader("Confronto di strategie passive per la riduzione dell'overheating", divider = True)
st.write("Caricamento... \nTempo stimato: 1 min")
    
# Comparison data frame
inputsRetrofit = ["BASE", "Schermature 0°", "Schermature 45°", "Ventilazione notturna"]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
    caso = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
    caso = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
    caso = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
    caso = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
else: 
    st.write(temp_df_tot.columns)

temp_df = pd.concat([temp_df_tot[caso], temp_df_tot["Trm-{}".format(city)], temp_df_tot["Tmax-{}".format(city)], temp_df_tot["TmaxVent-{}".format(city)], temp_df_tot["Tout-{}".format(city)], temp_df_tot["Month"], temp_df_tot["Day"], temp_df_tot["Day"], temp_df_tot["Weekday"], temp_df_tot["Hour"]], axis=1)

temp_df_compare = temp_df.copy()
temp_df_compare["BASE"] = temp_df[caso]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

dist_df_compare = dist_df_tot[dist_df_tot["Unnamed: 0"] == "bins"]
dist_df_compare = pd.concat([dist_df_compare, dist_df_tot[dist_df_tot["Unnamed: 0"] == casoDist]]) #, dist_df_tot[dist_df_tot["Unnamed: 0"] == "{} VENT".format(casoDist)]])

scenarios_df_compare = pd.DataFrame(columns=scenarios_df.columns)
scenarios_base = scenarios_df_tot[(scenarios_df_tot["window_to_floor_ratio"] == WFR/100) & (scenarios_df_tot["building_orientation"] == orient) & (scenarios_df_tot["solar_heat_gain_coefficient"] == SHGC) & (scenarios_df_tot["THERMAL"] == retrofit) & (scenarios_df_tot["VENT"] == vent)]

# Approximate WFR to 12 or 22
WFR_old = WFR
if WFR < 17:
    WFR = 12
else:
    WFR = 22

# Shading 00
temp_df_sh00       = pd.read_excel(get_file("RISULTATI-sh00",  f"Temperatures-{city}-{floor}.xlsx"))
scenarios_df_sh00  = pd.read_excel(get_file("RISULTATI-sh00",  f"Scenarios-{city}-{floor}.xlsx"))
dist_df_sh00       = pd.read_excel(get_file("RISULTATI-sh00",  f"Dist-{city}-{floor}.xlsx"))

temp_df_sh00['ts'] = pd.Timestamp('2025-01-01 00:00:00') + pd.to_timedelta(temp_df_sh00.index, unit='h')
temp_df_sh00["Month"] = temp_df_sh00["ts"].dt.month
temp_df_sh00["Day"] = temp_df_sh00["ts"].dt.day
temp_df_sh00["Weekday"] = temp_df_sh00["ts"].dt.weekday  # Monday=0, Sunday=6
temp_df_sh00["Hour"] = temp_df_sh00["ts"].dt.hour
temp_df_sh00 = temp_df_sh00.set_index("ts")

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh00:
    caso = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh00:
    caso = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh00:
    caso = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh00:
    caso = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

temp_sh00 = pd.DataFrame(temp_df_sh00[caso])

scenarios_sh00 = scenarios_df_sh00[(scenarios_df_sh00["window_to_floor_ratio"] == WFR/100) & (scenarios_df_sh00["building_orientation"] == orient) & (scenarios_df_sh00["solar_heat_gain_coefficient"] == SHGC) & (scenarios_df_sh00["THERMAL"] == retrofit) & (scenarios_df_sh00["VENT"] == vent)]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh00["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh00["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh00["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh00["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

dist_df_compare = pd.concat([dist_df_compare, dist_df_sh00[dist_df_sh00["Unnamed: 0"] == casoDist]]) #, dist_df_sh00[dist_df_sh00["Unnamed: 0"] == "{} VENT".format(casoDist)]])

# Shading 45
temp_df_sh45       = pd.read_excel(get_file("RISULTATI-sh45",  f"Temperatures-{city}-{floor}.xlsx"))
scenarios_df_sh45  = pd.read_excel(get_file("RISULTATI-sh45",  f"Scenarios-{city}-{floor}.xlsx"))
dist_df_sh45       = pd.read_excel(get_file("RISULTATI-sh45",  f"Dist-{city}-{floor}.xlsx"))

temp_df_sh45['ts'] = pd.Timestamp('2025-01-01 00:00:00') + pd.to_timedelta(temp_df_sh45.index, unit='h')
temp_df_sh45["Month"] = temp_df_sh45["ts"].dt.month
temp_df_sh45["Day"] = temp_df_sh45["ts"].dt.day
temp_df_sh45["Weekday"] = temp_df_sh45["ts"].dt.weekday  # Monday=0, Sunday=6
temp_df_sh45["Hour"] = temp_df_sh45["ts"].dt.hour
temp_df_sh45 = temp_df_sh45.set_index("ts")

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh45:
    caso = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh45:
    caso = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh45:
    caso = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh45:
    caso = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

temp_sh45 = temp_df_sh45[caso]

scenarios_sh45 = scenarios_df_sh45[(scenarios_df_sh45["window_to_floor_ratio"] == WFR/100) & (scenarios_df_sh45["building_orientation"] == orient) & (scenarios_df_sh45["solar_heat_gain_coefficient"] == SHGC) & (scenarios_df_sh45["THERMAL"] == retrofit) & (scenarios_df_sh45["VENT"] == vent)]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh45["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh45["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh45["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh45["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

dist_df_compare = pd.concat([dist_df_compare, dist_df_sh45[dist_df_sh45["Unnamed: 0"] == casoDist]]) #, dist_df_sh45[dist_df_sh45["Unnamed: 0"] == "{} VENT".format(casoDist)]])

# Night vent
temp_df_night      = pd.read_excel(get_file("RISULTATI-night", f"Temperatures-{city}-{floor}.xlsx"))
scenarios_df_night = pd.read_excel(get_file("RISULTATI-night", f"Scenarios-{city}-{floor}.xlsx"))
dist_df_night      = pd.read_excel(get_file("RISULTATI-night", f"Dist-{city}-{floor}.xlsx"))

temp_df_night['ts'] = pd.Timestamp('2025-01-01 00:00:00') + pd.to_timedelta(temp_df_night.index, unit='h')
temp_df_night["Month"] = temp_df_night["ts"].dt.month
temp_df_night["Day"] = temp_df_night["ts"].dt.day
temp_df_night["Weekday"] = temp_df_night["ts"].dt.weekday  # Monday=0, Sunday=6
temp_df_night["Hour"] = temp_df_night["ts"].dt.hour
temp_df_night = temp_df_night.set_index("ts")

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_night:
    caso = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_night:
    caso = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_night:
    caso = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_night:
    caso = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

temp_night = temp_df_night[caso]

scenarios_night = scenarios_df_night[(scenarios_df_night["window_to_floor_ratio"] == WFR/100) & (scenarios_df_night["building_orientation"] == orient) & (scenarios_df_night["solar_heat_gain_coefficient"] == SHGC) & (scenarios_df_night["THERMAL"] == retrofit) & (scenarios_df_night["VENT"] == vent)]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_night["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_night["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_night["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_night["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

dist_df_compare = pd.concat([dist_df_compare, dist_df_night[dist_df_night["Unnamed: 0"] == casoDist]]) #, dist_df_night[dist_df_night["Unnamed: 0"] == "{} VENT".format(casoDist)]])

#%% Comparison dataframe
temp_df_compare["Schermature 0°"] = temp_sh00
temp_df_compare["Schermature 45°"] = temp_sh45
temp_df_compare["Ventilazione notturna"] = temp_night

dist_df_compare.insert(1, "Caso", ["", "BASE", "Schermature 0°", "Schermature 45°", "Ventilazione notturna"])

scenarios_df_compare = pd.concat([scenarios_df_compare, scenarios_base, scenarios_sh00, scenarios_sh45, scenarios_night])
scenarios_df_compare.insert(1, "Caso", ["BASE", "Schermature 0°", "Schermature 45°", "Ventilazione notturna"])

number = len(inputsRetrofit)
diff = [-0.3, -0.1, 0.1, 0.3]

st.write("In the next charts, the following labels will be used:")

for element in inputsRetrofit:
    if element == "BASE":
        testo = "BASE = Configurazione iniziale"
    elif element == "Schermature 0°":
        testo = "0° = Schermature 0°"
    elif element == "Schermature 45°":
        testo = "45° = Schermature 45°"
    elif element == "Ventilazione notturna":
        testo = "NIGHT = Ventilazione notturna"
    
    st.markdown("- {}".format(testo))

# %% Display results - comfort bands
st.write("Percentuale di ore nelle categorie di comfort suddivise per periodi sulla base dell'accensione del riscaldamento e sulle vacanze estive. Confronto tra strategie passive.")
plt.rcParams.update({'font.size': 10})
periodCase = pd.DataFrame(index=[0, 1, 2, 3, 4], columns=["C1", "C2", "C3", "Overheating", "C1_VENT", "C2_VENT", "C3_VENT", "Overheating_VENT", "low", "lowBand3",
                          "lowBand2", "Band1", "highBand2", "highBand3", "high", "lowVent", "lowBand3Vent", "lowBand2Vent", "Band1Vent", "highBand2Vent", "highBand3Vent", "highVent"])

startSummer = "2025-06-15 00:00:00"
endSummer = "2025-09-15 00:00:00"

P1_mask = (temp_df.index >= "2025-01-01 00:00:00") & (temp_df.index < startNH)
P2_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer)
P3_mask = (temp_df.index >= startSummer) & (temp_df.index < endSummer)
P4_mask = (temp_df.index >= endSummer) & (temp_df.index < endNH)
P5_mask = (temp_df.index >= endNH) & (temp_df.index <= "2025-12-31 23:00:00")

fig, ax = plt.subplots()
fig.set_figheight(6)
fig.set_figwidth(9)
w = 0.5

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    if (comparazione == "BASE") | (comparazione == "WALL") | (comparazione == "ROOF") | (comparazione == "WINDOW"):
        iniziale = comparazione
    elif comparazione == "Schermature 0°":
        iniziale = "0°"
    elif comparazione == "Schermature 45°":
        iniziale = "45°"
    elif comparazione == "Ventilazione notturna":
        iniziale = "NIGHT"

    temp_comparazione = pd.concat(
        [temp_df_compare[comparazione], temp_df_compare["Tout-{}".format(city)]], axis=1)

    temp_df_P1 = temp_comparazione.loc[P1_mask].copy()
    temp_df_P2 = temp_comparazione.loc[P2_mask].copy()
    temp_df_P3 = temp_comparazione.loc[P3_mask].copy()
    temp_df_P4 = temp_comparazione.loc[P4_mask].copy()
    temp_df_P5 = temp_comparazione.loc[P5_mask].copy()

    temp_list = [temp_df_P1, temp_df_P2, temp_df_P3, temp_df_P4, temp_df_P5]
    nomi = ["Inizio dell'anno - \nspegnimento \nriscaldamento", "Spegnimento \nriscaldamento - \nfine della scuola",
            "Fine - inizio \ndella scuola", "Inizio della scuola - \naccensione \nriscaldamento", "Accensione \nriscaldamento - \nfine dell'anno"]

    for periodo in [0, 1, 2, 3, 4]:
        nomePeriodo = nomi[periodo]
        temp_period = temp_list[periodo]

        temp_period_case = temp_period[comparazione]
        temp_out_period = temp_period["Tout-{}".format(city)].values

        temp, Trm, Tmax, percentC1, percentC2, percentC3, overheating, Tmax_vent, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, dist_df_period, low, lowBand3, lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent = exceeding_hours_TM52(
            temp_out_period, temp_period_case, climatic_zone)

        # Save results
        lista = [percentC1, percentC2, percentC3, overheating, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, low, lowBand3,
                 lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent]
        periodCase.loc[periodo] = lista

    if inputsRetrofit[comparazione_numero] == "Increase air speed":
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 +
               diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["lowVent"], w/number, color="#90e0ef", label="T<Tmin")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 +
               diff[comparazione_numero]], periodCase["lowBand3Vent"],  w/number, bottom=periodCase["lowVent"], color="#ddead1", label="III fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["lowBand2Vent"],  w/number, bottom=periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#95bb72", label="II fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["Band1Vent"],  w/number, bottom=periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#4b6043", label="I fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["highBand2Vent"],  w/number, bottom=periodCase["Band1Vent"] + periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#95bb72")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["highBand3Vent"],
               w/number, bottom=periodCase["highBand2Vent"] + periodCase["Band1Vent"] + periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#ddead1")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["highVent"],  w/number,
               bottom=periodCase["highBand3Vent"] + periodCase["highBand2Vent"] + periodCase["Band1Vent"] + periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#f69697", label="T>Tmax")

    else:
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 +
               diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["low"], w/number, color="#90e0ef", label="T<Tmin")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 +
               diff[comparazione_numero]], periodCase["lowBand3"],  w/number, bottom=periodCase["low"], color="#ddead1", label="III fascia di comfort ")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 +
               diff[comparazione_numero]], periodCase["lowBand2"],  w/number, bottom=periodCase["lowBand3"] + periodCase["low"], color="#95bb72", label="II fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["Band1"],  w/number, bottom=periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#4b6043", label="I fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["highBand2"],  w/number, bottom=periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#95bb72")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["highBand3"],  w/number, bottom=periodCase["highBand2"] + periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#ddead1")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["high"],  w /
               number, bottom=periodCase["highBand3"] + periodCase["highBand2"] + periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#f69697", label="T>Tmax")
    handles, labels = ax.get_legend_handles_labels()

    ax.text(0 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(1 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(2 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(3 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(4 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)

ax.set_xticks([0, 1, 2, 3, 4], nomi)
ax.text(xgen, ypisl, "GEN", color=sns.mpl_palette("Set2")[2], ha="center")
ax.text(xfeb, ypisl, "FEB", color=sns.mpl_palette("Set2")[2], ha="center")
ax.text(xmar, ypisl, "MAR", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xapr, ypisl, "APR", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xmay, ypisl, "MAG", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xjun, ypisl, "GIU", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xjul, ypisl, "LUG", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xaug, ypisl, "AGO", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xsep, ypisl, "SET", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xoct, ypisl, "OTT", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xnov, ypisl, "NOV", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xdec, ypisl, "DIC", color=sns.mpl_palette("Set2")[2], ha="center")

ax.set_ylim(0, 100)
ax.text(-1, 50,
        "Percentuale di ore in ciascuna fascia di comfort [%]", rotation="vertical", va="center")

fig.legend(handles[:5], labels[:5], loc='upper center', ncol=7)

st.pyplot(fig)


# %% Display results - temperature distribution
st.write("Distribuzione di frequenza delle temperature sopra alla Tmax. Dati riferiti al periodo di spegnimento del riscaldamento nelle ore occupate. Confronto tra strategie passive.")

plt.rcParams.update({'font.size': 7})

fig, axs = plt.subplot_mosaic([['dist', 'scritte1'], ['dist', 'scritte2']], layout='constrained')
ax1 = axs["dist"]
ax2 = axs["scritte1"]
ax3 = axs["scritte2"]

fig.set_figheight(6)
fig.set_figwidth(9)

df_label = pd.DataFrame(index = ["Label"])
df_metrics = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)
df_metrics_tot = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)
df_metrics2 = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)
df_metrics_tot2 = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    if (comparazione == "BASE") | (comparazione == "WALL") | (comparazione == "ROOF") | (comparazione == "WINDOW"):
        iniziale = comparazione
    elif comparazione == "Schermature 0°":
        iniziale = "0°"
    elif comparazione == "Schermature 45°":
        iniziale = "45°"
    elif comparazione == "Ventilazione notturna":
        iniziale = "NIGHT"
    
    if comparazione == "BASE":
        WFR_new = WFR_old
    else:
        WFR_new = WFR
        
    dist_part = dist_df_compare[dist_df_compare["Caso"] == comparazione]
    
    if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC) in dist_part["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC)
    elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC) in dist_part["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC)
    elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC) in dist_part["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC)
    elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC) in dist_part["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC)
        
    
    temp_df = pd.concat([temp_df_compare[comparazione], temp_df_compare["Month"], temp_df_compare["Weekday"], temp_df_compare["Hour"],  temp_df_compare["Tmax-{}".format(city)],  temp_df_compare["TmaxVent-{}".format(city)]], axis = 1)
    temp_df["Occupied"] = (temp_df["Month"].isin(occupied_months) & temp_df["Weekday"].isin(occupied_weekdays) & temp_df["Hour"].isin(occupied_hours))

    ax1.plot(dist_df_compare[dist_df_compare["Unnamed: 0"] == "bins"].drop(columns=["Unnamed: 0", "Caso"]).values.flatten(), dist_df_compare[(dist_df_compare["Unnamed: 0"] == casoDist) & (dist_df_compare["Caso"] == comparazione)].drop(columns=["Unnamed: 0", "Caso"]).values.flatten()*100, label=iniziale, color=red[round(48/number*comparazione_numero)])
    
    # ALl non heating period
    nonheat_mask = (temp_df.index >= startNH) & (temp_df.index < endNH)
    df_nonheat = temp_df.loc[nonheat_mask].copy()
    df_occ = df_nonheat[df_nonheat["Occupied"]].copy()
    dist = np.where(df_occ[comparazione] > df_occ["Tmax-{}".format(city)],df_occ[comparazione] - df_occ["Tmax-{}".format(city)], 0)
    bins = np.arange(0, 11, 1).tolist()
    counts1, bins = np.histogram(dist)

    # School non heating period
    schoolNH_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer) | (temp_df.index > endSummer) & (temp_df.index < endNH)
    df_schoolNH = temp_df.loc[schoolNH_mask].copy()
    df_occ = df_schoolNH[df_schoolNH["Occupied"]].copy()
    dist = np.where(df_occ[comparazione] > df_occ["Tmax-{}".format(city)],df_occ[comparazione] - df_occ["Tmax-{}".format(city)], 0)
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
    
    df_label[comparazione] = iniziale
    df_metrics[comparazione] = [uno, tre]
    df_metrics_tot[comparazione] = [due, quattro]
    df_metrics2[comparazione] = [cinque, sette]
    df_metrics_tot2[comparazione] = [sei, otto]
    
    df_metrics = df_metrics.astype(float)
    df_metrics_tot = df_metrics_tot.astype(float)
    df_metrics2 = df_metrics2.astype(float)
    df_metrics_tot2 = df_metrics_tot2.astype(float)

    ax1.xaxis.set_tick_params(labelbottom=True)
    ax1.yaxis.set_tick_params(labelbottom=True)
    ax1.set_ylim(0, 100)
    ax1.set_xlim(0, 9)
    ax1.set_xticks(range(0, 10))

    ax1.set_xlabel("T - Tmax [°C]", ha='center')
    ax1.set_ylabel("Frequenza cumulata [%]", va='center', rotation='vertical')

df_label = df_label.transpose()
df_metrics = df_metrics.transpose()
df_metrics_tot = df_metrics_tot.transpose()
df_metrics2 = df_metrics2.transpose()
df_metrics_tot2 = df_metrics_tot2.transpose()

df_metrics = df_metrics.set_index(df_label["Label"])
df_metrics_tot = df_metrics_tot.set_index(df_label["Label"])
df_metrics2 = df_metrics2.set_index(df_label["Label"])
df_metrics_tot2 = df_metrics_tot2.set_index(df_label["Label"])

ax1.text(4.5, 103, "PERIODO NON RISCALDATO, ORE OCCUPATE", ha = "center", weight = "demi")    
ax1.axvspan(2, 9, alpha = 0.3, color = red[24], label = "Estremamente inaccettabile")
ax1.axhspan(0, 95, xmin = 0, xmax = 2/9, alpha = 0.3, color = red[12], label = "Inaccettabile")
ax1.axhspan(95, 100, xmin = 0, xmax = 2/9, alpha = 0.3, color=green[24], label = "Trascurabilmente inaccettabile")

if number >= 4:
    fig.legend(bbox_to_anchor=[0.5, 1.17], ncol=2, fontsize=10)
else:
    fig.legend(bbox_to_anchor=[0.5, 1.07], ncol=2, fontsize=10)

def wrap_labels3(df, ax, width):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width, break_long_words=False))
    ax.set_xticklabels(df.columns, rotation=0, fontsize=8) #df_label.loc["Label"]
    ax.set_yticklabels(df.index, fontsize=10)
    
im = ax2.matshow(df_metrics/df_metrics_tot, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax2.set_xticks(np.arange(len(df_metrics.columns)), minor=False)
ax2.set_yticks(np.arange(len(df_metrics.index)), minor=False)
ax2.xaxis.tick_top()
ax2.grid(which="minor", c='black', ls=':', lw='0.4')
ax2.set_xticks([x-0.5 for x in range(1, len(df_metrics.columns))], minor=True)
ax2.set_yticks([y-0.5 for y in range(1, len(df_metrics.index))], minor=True)
wrap_labels3(df_metrics, ax2, 5)

min_val, max_valRow = 0, 2
min_val, max_valCol = 0, number

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df_metrics[df_metrics.columns[j]][df_metrics.index[k]]
        t = df_metrics_tot[df_metrics_tot.columns[j]][df_metrics_tot.index[k]]
        ax2.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=8)
         
ax2.text(0.5, -1.3, "N° di ore con with T>Tmax / N° di ore totali", ha = "center", weight = "demi")

im = ax3.matshow(df_metrics2/df_metrics_tot2, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax3.set_xticks(np.arange(len(df_metrics2.columns)), minor=False)
ax3.set_yticks(np.arange(len(df_metrics2.index)), minor=False)
ax3.xaxis.tick_top()
ax3.grid(which="minor", c='black', ls=':', lw='0.4')
ax3.set_xticks([x-0.5 for x in range(1, len(df_metrics2.columns))], minor=True)
ax3.set_yticks([y-0.5 for y in range(1, len(df_metrics2.index))], minor=True)
wrap_labels3(df_metrics2, ax3, 5)

min_val, max_valRow = 0, 2
min_val, max_valCol = 0, number

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df_metrics[df_metrics2.columns[j]][df_metrics2.index[k]]
        t = df_metrics_tot[df_metrics_tot2.columns[j]][df_metrics_tot2.index[k]]
        ax3.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=8)
         
ax3.text(0.5, -1.3, "N° di ore con T>Tmax+2°C / N° di ore totali", ha = "center", weight = "demi")
st.pyplot(fig)


#%% Display results - TM52 compliance
st.write("Criteri di conformità con la norma TM52. Confronto tra strategie passive.")


fig, (ax1,ax2) = plt.subplots(1,2)
fig.set_figheight(6)
fig.set_figwidth(9)

Vent = pd.DataFrame(columns=["C1", "C2", "C3"])
noVent = pd.DataFrame(columns=["C1", "C2", "C3"])

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    if (comparazione == "BASE") | (comparazione == "WALL") | (comparazione == "ROOF") | (comparazione == "WINDOW"):
        iniziale = comparazione
    elif comparazione == "Schermature 0°":
        iniziale = "0°"
    elif comparazione == "Schermature 45°":
        iniziale = "45°"
    elif comparazione == "Ventilazione notturna":
        iniziale = "NIGHT"

    if comparazione == "BASE":
        WFR_new = WFR_old
    else:
        WFR_new = WFR
    
    noVent.loc[iniziale, "C1"] = float(scenarios_df_compare["C1"][(scenarios_df_compare["Caso"] == comparazione)].values[0])
    noVent.loc[iniziale, "C2"] = float(scenarios_df_compare["C2"][(scenarios_df_compare["Caso"] == comparazione)].values[0])
    noVent.loc[iniziale, "C3"] = float(scenarios_df_compare["C3"][(scenarios_df_compare["Caso"] == comparazione)].values[0])

    df = pd.concat([noVent, Vent])
    # df.index = ["Zero air speed", "Increased air speed"]
    df["TOT"] = 100
    df.loc[(df["C1"] == 0) | (df["C2"] == 0) | (df["C3"] == 0), "TOT"] = 0
    df = df.astype('float64')

criteri = pd.concat([df["C1"], df["C2"], df["C3"]], axis=1)
im = ax1.matshow(criteri, cmap="RdYlGn_r",interpolation="none", aspect = 0.5)
im.norm.autoscale([0, 100])
ax1.set_xticks(np.arange(len(criteri.columns)), minor=False)
ax1.set_yticks(np.arange(len(criteri.index)), minor=False)
ax1.xaxis.tick_top()
ax1.grid(which="minor", c='black', ls=':', lw='0.4')
ax1.set_xticks([x-0.5 for x in range(1, len(criteri.columns))], minor=True)
ax1.set_yticks([y-0.5 for y in range(1, len(criteri.index))], minor=True)
wrap_labels(criteri, ax1, 5)

min_val, max_valRow = 0, 3
min_val, max_valCol = 0, number

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df[criteri.columns[j]][criteri.index[k]]
        ax1.text(j, k, "{}%".format(str(round(c, 1))), va='center', ha='center', fontsize=10)

tot = pd.DataFrame(df["TOT"])
tot = tot.astype(float)    
im = ax2.matshow(tot, cmap="RdYlGn_r", interpolation="none", aspect = 0.5/3)
im.norm.autoscale([0, 100])
ax2.set_xticks(np.arange(len(tot.columns)), minor=False)
ax2.set_yticks(np.arange(len(tot.index)), minor=False)
ax2.xaxis.tick_top()
ax2.grid(which="minor", c='black', ls=':', lw='0.4')
ax2.set_xticks([x-0.5 for x in range(1, len(tot.columns))], minor=True)
ax2.set_yticks([y-0.5 for y in range(1, len(tot.index))], minor=True)
wrap_labels2(tot, ax2, 5)

truefalse(1, number, tot, ax2)

st.pyplot(fig)

# %% Calculate share of overheating days
st.write("Giorni totali di stress termico e giorni di stress termico per il periodo scolastico di spegnimento del riscaldamento. Confronto tra strategie passive.")


heat_stress = pd.DataFrame(columns = ["Giorni di stress termico totali", "Giorni di stress termico periodo scolastico non riscaldato"], index = range(number))
heat_stress_tot = pd.DataFrame(columns = ["Giorni di stress termico totali", "Giorni di stress termico periodo scolastico non riscaldato"], index = range(number))
indice = pd.DataFrame(columns = ["caso"], index = range(number))

scenarios_df_compare["Overheating days share"] = ""
scenarios_df_compare["Overheating days share with increased air speed"] = ""

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    if (comparazione == "BASE") | (comparazione == "WALL") | (comparazione == "ROOF") | (comparazione == "WINDOW"):
        iniziale = comparazione
    elif comparazione == "Schermature 0°":
        iniziale = "0°"
    elif comparazione == "Schermature 45°":
        iniziale = "45°"
    elif comparazione == "Ventilazione notturna":
        iniziale = "NIGHT"

    if comparazione == "SHGC reduction":
        SHGC_new = 0.3
        retrofit_new = retrofit
        vent_new = vent
    else:
        SHGC_new = SHGC
        if comparazione == "Walls insulation":
            retrofit_new = "WALL"
        elif comparazione == "Roof insulation":
            retrofit_new = "ROOF"
        elif comparazione == "Double glazings":
            retrofit_new = "WINDOW"
        else:
            retrofit_new = retrofit
        if comparazione == "Increase ventilation rate":
            vent_new = "8 l/s/pers"
        else:
            vent_new = vent

    if comparazione != "Increase air speed":
        temp_comparazione = pd.concat([temp_df_compare[comparazione], temp_df_compare["Tout-{}".format(city)], temp_df_compare["Tmax-{}".format(
            city)], temp_df_compare["TmaxVent-{}".format(city)], temp_df_compare["Trm-{}".format(city)]], axis=1)

        # Days in which ventilation is feasible = days in which at ALL hours the temperature outside is lower than the indoor one and lower than the threshold
        vent_comparazione = pd.DataFrame(
            0, index=temp_comparazione.index, columns=temp_comparazione.columns)

        vent_comparazione.loc[(temp_comparazione["Tout-{}".format(city)] < temp_comparazione["Tmax-{}".format(city)] - 7)
                              & (temp_comparazione["Tout-{}".format(city)] < temp_comparazione[comparazione]), comparazione] = 1

        vent_daily = vent_comparazione.resample("1440min").sum()
        temp_daily = temp_comparazione.resample("1440min").max()

        heat_comparazione = pd.DataFrame(
            0, index=temp_daily.index, columns=temp_daily.columns)
        heat_comparazione = heat_comparazione.drop(columns=["Tmax-{}".format(
            city), "TmaxVent-{}".format(city), "Tout-{}".format(city), "Trm-{}".format(city)])

        # Share of days in which indoor temperature is above the threshold and ventilation is not feasible, or in which Trm is above 30°C (limit of the adaptive chart)
        heat_comparazione.loc[((temp_daily[comparazione] > temp_daily["Tmax-{}".format(city)]) | (
            temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[comparazione] < 24), comparazione] = 1

        share = heat_comparazione.sum(axis=0) / 365 * 100

        # At least 3 consecutive days to be considered heat wave
        heat_comparazione_updated = heat_comparazione.copy()

        for day in heat_comparazione.index:
            if (day == pd.Timestamp('2025-01-01 00:00:00')) | (day == pd.Timestamp('2025-01-02 00:00:00')) | (day == pd.Timestamp('2025-12-30 00:00:00')) | (day == pd.Timestamp('2025-12-31 00:00:00')):
                ieri = 0
                laltroieri = 0
                oggi = heat_comparazione[comparazione][day]
                domani = 0
                dopodomani = 0
            else:
                laltroieri = heat_comparazione[comparazione][day -
                                                             pd.to_timedelta(2, unit='D')]
                ieri = heat_comparazione[comparazione][day -
                                                       pd.to_timedelta(1, unit='D')]
                oggi = heat_comparazione[comparazione][day]
                domani = heat_comparazione[comparazione][day +
                                                         pd.to_timedelta(1, unit='D')]
                dopodomani = heat_comparazione[comparazione][day +
                                                             pd.to_timedelta(2, unit='D')]

            if oggi == 1:
                if ((domani == 1) & (dopodomani == 1)) | ((ieri == 1) & (laltroieri == 1)) | ((ieri == 1) & (domani == 1)):
                    heat_comparazione_updated.loc[day, comparazione] = 1
                else:
                    heat_comparazione_updated.loc[day, comparazione] = 0

        share_updated = float(
            heat_comparazione_updated.sum(axis=0).values[0]) / 365 * 100
        # scenarios_df_compare["Overheating days share"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)] = float(heat_comparazione_updated.sum(axis = 0).values) / 365 * 100
        
        numeroTOT = round(heat_comparazione_updated.sum(axis=0)[comparazione])
        schoolNH_mask_daily = (heat_comparazione_updated.index >= startNH) & (heat_comparazione_updated.index < startSummer) | (heat_comparazione_updated.index > endSummer) & (heat_comparazione_updated.index < endNH)
        heat_comparazione_scuola = heat_comparazione_updated.loc[schoolNH_mask_daily].copy()
        numeroESTATE = round(heat_comparazione_scuola.sum(axis=0)[comparazione])
        
    else:
        comparazione = "BASE"
        temp_comparazione = pd.concat([temp_df_compare[comparazione], temp_df_compare["Tout-{}".format(city)], temp_df_compare["Tmax-{}".format(
            city)], temp_df_compare["TmaxVent-{}".format(city)], temp_df_compare["Trm-{}".format(city)]], axis=1)

        # Days in which ventilation is feasible = days in which at ALL hours the temperature outside is lower than the indoor one and lower than the threshold
        vent_comparazione = pd.DataFrame(
            0, index=temp_comparazione.index, columns=temp_comparazione.columns)

        vent_comparazione.loc[(temp_comparazione["Tout-{}".format(city)] < temp_comparazione["Tmax-{}".format(city)] - 7)
                              & (temp_comparazione["Tout-{}".format(city)] < temp_comparazione[comparazione]), comparazione] = 1

        vent_daily = vent_comparazione.resample("1440min").sum()
        temp_daily = temp_comparazione.resample("1440min").max()

        heat_comparazione = pd.DataFrame(
            0, index=temp_daily.index, columns=temp_daily.columns)
        heat_comparazione = heat_comparazione.drop(columns=["Tmax-{}".format(
            city), "TmaxVent-{}".format(city), "Tout-{}".format(city), "Trm-{}".format(city)])
        heat_comparazione_vent = heat_comparazione.copy()

        # Share of days in which indoor temperature is above the threshold and ventilation is not feasible, or in which Trm is above 30°C (limit of the adaptive chart)
        heat_comparazione_vent.loc[((temp_daily[comparazione] > temp_daily["TmaxVent-{}".format(city)]) | (
            temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[comparazione] < 24), comparazione] = 1

        share = heat_comparazione.sum(axis=0) / 365 * 100

        # At least 3 consecutive days to be considered heat wave
        heat_comparazione_vent_updated = heat_comparazione_vent.copy()

        for day in heat_comparazione_vent.index:
            if (day == pd.Timestamp('2025-01-01 00:00:00')) | (day == pd.Timestamp('2025-01-02 00:00:00')) | (day == pd.Timestamp('2025-12-30 00:00:00')) | (day == pd.Timestamp('2025-12-31 00:00:00')):
                ieri = 0
                laltroieri = 0
                oggi = heat_comparazione_vent[comparazione][day]
                domani = 0
                dopodomani = 0
            else:
                laltroieri = heat_comparazione_vent[comparazione][day -
                                                                  pd.to_timedelta(2, unit='D')]
                ieri = heat_comparazione_vent[comparazione][day -
                                                            pd.to_timedelta(1, unit='D')]
                oggi = heat_comparazione_vent[comparazione][day]
                domani = heat_comparazione_vent[comparazione][day +
                                                              pd.to_timedelta(1, unit='D')]
                dopodomani = heat_comparazione_vent[comparazione][day +
                                                                  pd.to_timedelta(2, unit='D')]

            if oggi == 1:
                if ((domani == 1) & (dopodomani == 1)) | ((ieri == 1) & (laltroieri == 1)) | ((ieri == 1) & (domani == 1)):
                    heat_comparazione_vent_updated.loc[day, comparazione] = 1
                else:
                    heat_comparazione_vent_updated.loc[day, comparazione] = 0

        share_updated = float(
            heat_comparazione_vent_updated.sum(axis=0).values[0]) / 365 * 100
        # scenarios_df_compare["Overheating days share with increased air speed"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)] = float(heat_comparazione_vent_updated.sum(axis = 0).values) / 365 * 100
        
        numeroTOT = round(heat_comparazione_vent_updated.sum(axis=0)[comparazione])
        schoolNH_mask_daily = (heat_comparazione_vent_updated.index >= startNH) & (heat_comparazione_vent_updated.index < startSummer) | (heat_comparazione_updated.index > endSummer) & (heat_comparazione_updated.index < endNH)
        heat_comparazione_vent_scuola = heat_comparazione_vent_updated.loc[schoolNH_mask_daily].copy()
        numeroESTATE = round(heat_comparazione_vent_scuola.sum(axis=0)[comparazione])
    
    indice.loc[comparazione_numero] = [iniziale]        
    heat_stress.loc[comparazione_numero] = [numeroTOT, numeroESTATE]
    heat_stress = heat_stress.astype(float)
    heat_stress_tot.loc[comparazione_numero] = [365, heat_df_scuola.shape[0]]
    
heat_stress = heat_stress.set_index(indice["caso"])
heat_stress_tot = heat_stress_tot.set_index(indice["caso"])

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

def numeri2(max_valRow, max_valCol, df, dftot, ax):
    for j in range(max_valRow):
        for k in range(max_valCol):
            c = df[df.columns[j]][df.index[k]]
            t = dftot[dftot.columns[j]][dftot.index[k]]
            ax.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=12)

numeri2(2, number, heat_stress, heat_stress_tot, ax)

st.pyplot(fig)

#%% Same thing with future weather and UHI
st.subheader("Confronto proiezioni clima futuro e effetto isola di calore", divider = True)
st.write("Caricamento... \nTempo stimato: 1 min")

temp_df_2050       = pd.read_excel(get_file("RISULTATI-2050", f"Temperatures-{city}-{floor}-2050.xlsx"))
scenarios_df_2050  = pd.read_excel(get_file("RISULTATI-2050", f"Scenarios-{city}-{floor}-2050.xlsx"))
dist_df_2050       = pd.read_excel(get_file("RISULTATI-2050", f"Dist-{city}-{floor}-2050.xlsx"))

temp_df_2080       = pd.read_excel(get_file("RISULTATI-2080", f"Temperatures-{city}-{floor}-2080.xlsx"))
scenarios_df_2080  = pd.read_excel(get_file("RISULTATI-2080", f"Scenarios-{city}-{floor}-2080.xlsx"))
dist_df_2080       = pd.read_excel(get_file("RISULTATI-2080", f"Dist-{city}-{floor}-2080.xlsx"))

temp_df_UHI        = pd.read_excel(get_file("RISULTATI-UHI",  f"Temperatures-{city}-{floor}-UHI.xlsx"))
scenarios_df_UHI   = pd.read_excel(get_file("RISULTATI-UHI",  f"Scenarios-{city}-{floor}-UHI.xlsx"))
dist_df_UHI        = pd.read_excel(get_file("RISULTATI-UHI",  f"Dist-{city}-{floor}-UHI.xlsx"))

temp_df_sh00 = temp_df_2050
temp_df_sh45 = temp_df_2080
temp_df_night = temp_df_UHI
    
# Comparison data frame
inputsRetrofit = ["BASE", "2050", "2080", "UHI"]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
    caso = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
    caso = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
    caso = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_tot:
    caso = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
else: 
    st.write(temp_df_tot.columns)

temp_df = pd.concat([temp_df_tot[caso], temp_df_tot["Trm-{}".format(city)], temp_df_tot["Tmax-{}".format(city)], temp_df_tot["TmaxVent-{}".format(city)], temp_df_tot["Tout-{}".format(city)], temp_df_tot["Month"], temp_df_tot["Day"], temp_df_tot["Day"], temp_df_tot["Weekday"], temp_df_tot["Hour"]], axis=1)

temp_df_compare = temp_df.copy()
temp_df_compare["BASE"] = temp_df[caso]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_tot["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

dist_df_compare = dist_df_tot[dist_df_tot["Unnamed: 0"] == "bins"]
dist_df_compare = pd.concat([dist_df_compare, dist_df_tot[dist_df_tot["Unnamed: 0"] == casoDist]]) #, dist_df_tot[dist_df_tot["Unnamed: 0"] == "{} VENT".format(casoDist)]])

scenarios_df_compare = pd.DataFrame(columns=scenarios_df.columns)
scenarios_base = scenarios_df_tot[(scenarios_df_tot["window_to_floor_ratio"] == WFR/100) & (scenarios_df_tot["building_orientation"] == orient) & (scenarios_df_tot["solar_heat_gain_coefficient"] == SHGC) & (scenarios_df_tot["THERMAL"] == retrofit) & (scenarios_df_tot["VENT"] == vent)]

# Approximate WFR to 12 or 22
WFR_old = WFR
if WFR < 17:
    WFR = 12
else:
    WFR = 22

# Future 2050
weather = "2050"
temp_df_sh00['ts'] = pd.Timestamp('2025-01-01 00:00:00') + pd.to_timedelta(temp_df_sh00.index, unit='h')
temp_df_sh00["Month"] = temp_df_sh00["ts"].dt.month
temp_df_sh00["Day"] = temp_df_sh00["ts"].dt.day
temp_df_sh00["Weekday"] = temp_df_sh00["ts"].dt.weekday  # Monday=0, Sunday=6
temp_df_sh00["Hour"] = temp_df_sh00["ts"].dt.hour
temp_df_sh00 = temp_df_sh00.set_index("ts")

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh00:
    caso = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh00:
    caso = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh00:
    caso = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh00:
    caso = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

temp_sh00 = pd.DataFrame(temp_df_sh00[caso])

scenarios_sh00 = scenarios_df_sh00[(scenarios_df_sh00["window_to_floor_ratio"] == WFR/100) & (scenarios_df_sh00["building_orientation"] == orient) & (scenarios_df_sh00["solar_heat_gain_coefficient"] == SHGC) & (scenarios_df_sh00["THERMAL"] == retrofit) & (scenarios_df_sh00["VENT"] == vent)]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh00["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh00["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh00["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh00["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

dist_df_compare = pd.concat([dist_df_compare, dist_df_sh00[dist_df_sh00["Unnamed: 0"] == casoDist]]) #, dist_df_sh00[dist_df_sh00["Unnamed: 0"] == "{} VENT".format(casoDist)]])

# Future 2080
weather = "2080"
temp_df_sh45['ts'] = pd.Timestamp('2025-01-01 00:00:00') + pd.to_timedelta(temp_df_sh45.index, unit='h')
temp_df_sh45["Month"] = temp_df_sh45["ts"].dt.month
temp_df_sh45["Day"] = temp_df_sh45["ts"].dt.day
temp_df_sh45["Weekday"] = temp_df_sh45["ts"].dt.weekday  # Monday=0, Sunday=6
temp_df_sh45["Hour"] = temp_df_sh45["ts"].dt.hour
temp_df_sh45 = temp_df_sh45.set_index("ts")

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh45:
    caso = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh45:
    caso = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh45:
    caso = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_sh45:
    caso = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

temp_sh45 = temp_df_sh45[caso]

scenarios_sh45 = scenarios_df_sh45[(scenarios_df_sh45["window_to_floor_ratio"] == WFR/100) & (scenarios_df_sh45["building_orientation"] == orient) & (scenarios_df_sh45["solar_heat_gain_coefficient"] == SHGC) & (scenarios_df_sh45["THERMAL"] == retrofit) & (scenarios_df_sh45["VENT"] == vent)]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh45["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh45["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh45["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_sh45["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

dist_df_compare = pd.concat([dist_df_compare, dist_df_sh45[dist_df_sh45["Unnamed: 0"] == casoDist]]) #, dist_df_sh45[dist_df_sh45["Unnamed: 0"] == "{} VENT".format(casoDist)]])

# UHI
weather = "UHI"
temp_df_night['ts'] = pd.Timestamp('2025-01-01 00:00:00') + pd.to_timedelta(temp_df_night.index, unit='h')
temp_df_night["Month"] = temp_df_night["ts"].dt.month
temp_df_night["Day"] = temp_df_night["ts"].dt.day
temp_df_night["Weekday"] = temp_df_night["ts"].dt.weekday  # Monday=0, Sunday=6
temp_df_night["Hour"] = temp_df_night["ts"].dt.hour
temp_df_night = temp_df_night.set_index("ts")

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_night:
    caso = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_night:
    caso = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_night:
    caso = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in temp_df_night:
    caso = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

temp_night = temp_df_night[caso]

scenarios_night = scenarios_df_night[(scenarios_df_night["window_to_floor_ratio"] == WFR/100) & (scenarios_df_night["building_orientation"] == orient) & (scenarios_df_night["solar_heat_gain_coefficient"] == SHGC) & (scenarios_df_night["THERMAL"] == retrofit) & (scenarios_df_night["VENT"] == vent)]

if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_night["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_night["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_night["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)
elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC) in dist_df_night["Unnamed: 0"].values:
    casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR, orient, SHGC)

dist_df_compare = pd.concat([dist_df_compare, dist_df_night[dist_df_night["Unnamed: 0"] == casoDist]]) #, dist_df_night[dist_df_night["Unnamed: 0"] == "{} VENT".format(casoDist)]])

#%% Comparison dataframe
temp_df_compare["2050"] = temp_sh00
temp_df_compare["2080"] = temp_sh45
temp_df_compare["UHI"] = temp_night

dist_df_compare.insert(1, "Caso", ["", "BASE", "2050", "2080", "UHI"])

scenarios_df_compare = pd.concat([scenarios_df_compare, scenarios_base, scenarios_sh00, scenarios_sh45, scenarios_night])
scenarios_df_compare.insert(1, "Caso", ["BASE", "2050", "2080", "UHI"])

number = len(inputsRetrofit)
diff = [-0.3, -0.1, 0.1, 0.3]

st.write("In the next charts, the following labels will be used:")

for element in inputsRetrofit:
    if element == "BASE":
        testo = "BASE = Configurazione iniziale"
    elif element == "2050":
        testo = "2050 = proiezione clima futuro 2050 con scenario SSP5-8.5"
    elif element == "2080":
        testo = "2080 = proiezione clima futuro 2080 con scenario SSP5-8.5"
    elif element == "UHI":
        testo = "UHI = effetto isola di calore"
    
    st.markdown("- {}".format(testo))

# %% Display results - comfort bands
st.write("Percentuale di ore nelle categorie di comfort suddivise per periodi sulla base dell'accensione del riscaldamento e sulle vacanze estive. Confronto tra scenari climatici.")
plt.rcParams.update({'font.size': 10})
periodCase = pd.DataFrame(index=[0, 1, 2, 3, 4], columns=["C1", "C2", "C3", "Overheating", "C1_VENT", "C2_VENT", "C3_VENT", "Overheating_VENT", "low", "lowBand3",
                          "lowBand2", "Band1", "highBand2", "highBand3", "high", "lowVent", "lowBand3Vent", "lowBand2Vent", "Band1Vent", "highBand2Vent", "highBand3Vent", "highVent"])

startSummer = "2025-06-15 00:00:00"
endSummer = "2025-09-15 00:00:00"

P1_mask = (temp_df.index >= "2025-01-01 00:00:00") & (temp_df.index < startNH)
P2_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer)
P3_mask = (temp_df.index >= startSummer) & (temp_df.index < endSummer)
P4_mask = (temp_df.index >= endSummer) & (temp_df.index < endNH)
P5_mask = (temp_df.index >= endNH) & (temp_df.index <= "2025-12-31 23:00:00")

fig, ax = plt.subplots()
fig.set_figheight(6)
fig.set_figwidth(9)
w = 0.5

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    iniziale = comparazione

    temp_comparazione = pd.concat(
        [temp_df_compare[comparazione], temp_df_compare["Tout-{}".format(city)]], axis=1)

    temp_df_P1 = temp_comparazione.loc[P1_mask].copy()
    temp_df_P2 = temp_comparazione.loc[P2_mask].copy()
    temp_df_P3 = temp_comparazione.loc[P3_mask].copy()
    temp_df_P4 = temp_comparazione.loc[P4_mask].copy()
    temp_df_P5 = temp_comparazione.loc[P5_mask].copy()

    temp_list = [temp_df_P1, temp_df_P2, temp_df_P3, temp_df_P4, temp_df_P5]
    nomi = ["Inizio dell'anno - \nspegnimento \nriscaldamento", "Spegnimento \nriscaldamento - \nfine della scuola",
            "Fine - inizio \ndella scuola", "Inizio della scuola - \naccensione \nriscaldamento", "Accensione \nriscaldamento - \nfine dell'anno"]

    for periodo in [0, 1, 2, 3, 4]:
        nomePeriodo = nomi[periodo]
        temp_period = temp_list[periodo]

        temp_period_case = temp_period[comparazione]
        temp_out_period = temp_period["Tout-{}".format(city)].values

        temp, Trm, Tmax, percentC1, percentC2, percentC3, overheating, Tmax_vent, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, dist_df_period, low, lowBand3, lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent = exceeding_hours_TM52(
            temp_out_period, temp_period_case, climatic_zone)

        # Save results
        lista = [percentC1, percentC2, percentC3, overheating, percentC1Vent, percentC2Vent, percentC3Vent, overheatingVent, low, lowBand3,
                 lowBand2, Band1, highBand2, highBand3, high, lowVent, lowBand3Vent, lowBand2Vent, Band1Vent, highBand2Vent, highBand3Vent, highVent]
        periodCase.loc[periodo] = lista

    if inputsRetrofit[comparazione_numero] == "Increase air speed":
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 +
               diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["lowVent"], w/number, color="#90e0ef", label="T<Tmin")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 +
               diff[comparazione_numero]], periodCase["lowBand3Vent"],  w/number, bottom=periodCase["lowVent"], color="#ddead1", label="III fascia di comfort ")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["lowBand2Vent"],  w/number, bottom=periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#95bb72", label="II fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["Band1Vent"],  w/number, bottom=periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#4b6043", label="I fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["highBand2Vent"],  w/number, bottom=periodCase["Band1Vent"] + periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#95bb72")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["highBand3Vent"],
               w/number, bottom=periodCase["highBand2Vent"] + periodCase["Band1Vent"] + periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#ddead1")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["highVent"],  w/number,
               bottom=periodCase["highBand3Vent"] + periodCase["highBand2Vent"] + periodCase["Band1Vent"] + periodCase["lowBand2Vent"] + periodCase["lowBand3Vent"] + periodCase["lowVent"], color="#f69697", label="T>Tmax")

    else:
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 +
               diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["low"], w/number, color="#90e0ef", label="T<Tmin")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 +
               diff[comparazione_numero]], periodCase["lowBand3"],  w/number, bottom=periodCase["low"], color="#ddead1", label="III fascia di comfort ")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 +
               diff[comparazione_numero]], periodCase["lowBand2"],  w/number, bottom=periodCase["lowBand3"] + periodCase["low"], color="#95bb72", label="II fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["Band1"],  w/number, bottom=periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#4b6043", label="I fascia di comfort")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["highBand2"],  w/number, bottom=periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#95bb72")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]],
               periodCase["highBand3"],  w/number, bottom=periodCase["highBand2"] + periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#ddead1")
        ax.bar([0 + diff[comparazione_numero], 1 + diff[comparazione_numero], 2 + diff[comparazione_numero], 3 + diff[comparazione_numero], 4 + diff[comparazione_numero]], periodCase["high"],  w /
               number, bottom=periodCase["highBand3"] + periodCase["highBand2"] + periodCase["Band1"] + periodCase["lowBand2"] + periodCase["lowBand3"] + periodCase["low"], color="#f69697", label="T>Tmax")
    handles, labels = ax.get_legend_handles_labels()

    ax.text(0 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(1 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(2 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(3 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)
    ax.text(4 + diff[comparazione_numero], 102, iniziale,
            ha="center", rotation="vertical", fontsize=5)

ax.set_xticks([0, 1, 2, 3, 4], nomi)
ax.text(xgen, ypisl, "GEN", color=sns.mpl_palette("Set2")[2], ha="center")
ax.text(xfeb, ypisl, "FEB", color=sns.mpl_palette("Set2")[2], ha="center")
ax.text(xmar, ypisl, "MAR", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xapr, ypisl, "APR", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xmay, ypisl, "MAG", color=sns.mpl_palette("Set2")[3], ha="center")
ax.text(xjun, ypisl, "GIU", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xjul, ypisl, "LUG", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xaug, ypisl, "AGO", color=sns.mpl_palette("Set2")[5], ha="center")
ax.text(xsep, ypisl, "SET", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xoct, ypisl, "OTT", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xnov, ypisl, "NOV", color=sns.mpl_palette("Set2")[4], ha="center")
ax.text(xdec, ypisl, "DIC", color=sns.mpl_palette("Set2")[2], ha="center")

ax.set_ylim(0, 100)
ax.text(-1, 50,
        "Share of hours in each comfort band [%]", rotation="vertical", va="center")

fig.legend(handles[:5], labels[:5], loc='upper center', ncol=7)

st.pyplot(fig)


# %% Display results - temperature distribution
st.write("Distribuzione di frequenza delle temperature sopra alla Tmax. Dati riferiti al periodo di spegnimento del riscaldamento nelle ore occupate. Confronto tra scenari climatici.")

plt.rcParams.update({'font.size': 7})

fig, axs = plt.subplot_mosaic([['dist', 'scritte1'], ['dist', 'scritte2']], layout='constrained')
ax1 = axs["dist"]
ax2 = axs["scritte1"]
ax3 = axs["scritte2"]

fig.set_figheight(6)
fig.set_figwidth(9)

df_label = pd.DataFrame(index = ["Label"])
df_metrics = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)
df_metrics_tot = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)
df_metrics2 = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)
df_metrics_tot2 = pd.DataFrame(index = ["Periodo non riscaldato", "Periodo scolastico non riscaldato"], columns = inputsRetrofit)

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    iniziale = comparazione
    
    if comparazione == "BASE":
        WFR_new = WFR_old
    else:
        WFR_new = WFR
        
    dist_part = dist_df_compare[dist_df_compare["Caso"] == comparazione]
    
    if "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC) in dist_part["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}, {}, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC)
    elif "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC) in dist_part["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}, {}.0, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC)
    elif "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC) in dist_part["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}.0, {}, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC)
    elif "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC) in dist_part["Unnamed: 0"].values:
        casoDist = "-{}, {}, {}, {}, {}.0, {}.0, {}".format(city, floor, vent, retrofit, WFR_new, orient, SHGC)
        
    
    temp_df = pd.concat([temp_df_compare[comparazione], temp_df_compare["Month"], temp_df_compare["Weekday"], temp_df_compare["Hour"],  temp_df_compare["Tmax-{}".format(city)],  temp_df_compare["TmaxVent-{}".format(city)]], axis = 1)
    temp_df["Occupied"] = (temp_df["Month"].isin(occupied_months) & temp_df["Weekday"].isin(occupied_weekdays) & temp_df["Hour"].isin(occupied_hours))

    ax1.plot(dist_df_compare[dist_df_compare["Unnamed: 0"] == "bins"].drop(columns=["Unnamed: 0", "Caso"]).values.flatten(), dist_df_compare[(dist_df_compare["Unnamed: 0"] == casoDist) & (dist_df_compare["Caso"] == comparazione)].drop(columns=["Unnamed: 0", "Caso"]).values.flatten()*100, label=iniziale, color=red[round(48/number*comparazione_numero)])
    
    # ALl non heating period
    nonheat_mask = (temp_df.index >= startNH) & (temp_df.index < endNH)
    df_nonheat = temp_df.loc[nonheat_mask].copy()
    df_occ = df_nonheat[df_nonheat["Occupied"]].copy()
    dist = np.where(df_occ[comparazione] > df_occ["Tmax-{}".format(city)],df_occ[comparazione] - df_occ["Tmax-{}".format(city)], 0)
    bins = np.arange(0, 11, 1).tolist()
    counts1, bins = np.histogram(dist)

    # School non heating period
    schoolNH_mask = (temp_df.index >= startNH) & (temp_df.index < startSummer) | (temp_df.index > endSummer) & (temp_df.index < endNH)
    df_schoolNH = temp_df.loc[schoolNH_mask].copy()
    df_occ = df_schoolNH[df_schoolNH["Occupied"]].copy()
    dist = np.where(df_occ[comparazione] > df_occ["Tmax-{}".format(city)],df_occ[comparazione] - df_occ["Tmax-{}".format(city)], 0)
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
    
    df_label[comparazione] = iniziale
    df_metrics[comparazione] = [uno, tre]
    df_metrics_tot[comparazione] = [due, quattro]
    df_metrics2[comparazione] = [cinque, sette]
    df_metrics_tot2[comparazione] = [sei, otto]
    
    df_metrics = df_metrics.astype(float)
    df_metrics_tot = df_metrics_tot.astype(float)
    df_metrics2 = df_metrics2.astype(float)
    df_metrics_tot2 = df_metrics_tot2.astype(float)

    ax1.xaxis.set_tick_params(labelbottom=True)
    ax1.yaxis.set_tick_params(labelbottom=True)
    ax1.set_ylim(0, 100)
    ax1.set_xlim(0, 9)
    ax1.set_xticks(range(0, 10))

    ax1.set_xlabel("T - Tmax [°C]", ha='center')
    ax1.set_ylabel("Frequenza cumulata [%]", va='center', rotation='vertical')

df_label = df_label.transpose()
df_metrics = df_metrics.transpose()
df_metrics_tot = df_metrics_tot.transpose()
df_metrics2 = df_metrics2.transpose()
df_metrics_tot2 = df_metrics_tot2.transpose()

df_metrics = df_metrics.set_index(df_label["Label"])
df_metrics_tot = df_metrics_tot.set_index(df_label["Label"])
df_metrics2 = df_metrics2.set_index(df_label["Label"])
df_metrics_tot2 = df_metrics_tot2.set_index(df_label["Label"])

ax1.text(4.5, 103, "PERIODO NON RISCALDATO, ORE OCCUPATE", ha = "center", weight = "demi")    
ax1.axvspan(2, 9, alpha = 0.3, color = red[24], label = "Estremamente inaccettabile")
ax1.axhspan(0, 95, xmin = 0, xmax = 2/9, alpha = 0.3, color = red[12], label = "Inaccettabile")
ax1.axhspan(95, 100, xmin = 0, xmax = 2/9, alpha = 0.3, color=green[24], label = "Trascurabilmente inaccettabile")

if number >= 4:
    fig.legend(bbox_to_anchor=[0.5, 1.17], ncol=2, fontsize=10)
else:
    fig.legend(bbox_to_anchor=[0.5, 1.07], ncol=2, fontsize=10)

def wrap_labels3(df, ax, width):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width, break_long_words=False))
    ax.set_xticklabels(df.columns, rotation=0, fontsize=8) #df_label.loc["Label"]
    ax.set_yticklabels(df.index, fontsize=10)
    
im = ax2.matshow(df_metrics/df_metrics_tot, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax2.set_xticks(np.arange(len(df_metrics.columns)), minor=False)
ax2.set_yticks(np.arange(len(df_metrics.index)), minor=False)
ax2.xaxis.tick_top()
ax2.grid(which="minor", c='black', ls=':', lw='0.4')
ax2.set_xticks([x-0.5 for x in range(1, len(df_metrics.columns))], minor=True)
ax2.set_yticks([y-0.5 for y in range(1, len(df_metrics.index))], minor=True)
wrap_labels3(df_metrics, ax2, 5)

min_val, max_valRow = 0, 2
min_val, max_valCol = 0, number

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df_metrics[df_metrics.columns[j]][df_metrics.index[k]]
        t = df_metrics_tot[df_metrics_tot.columns[j]][df_metrics_tot.index[k]]
        ax2.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=8)
         
ax2.text(0.5, -1.3, "N° di ore con T>Tmax / N° di ore totali", ha = "center", weight = "demi")

im = ax3.matshow(df_metrics2/df_metrics_tot2, cmap="RdYlGn_r", interpolation="none", aspect = 0.25)
im.norm.autoscale([0, massimo])
ax3.set_xticks(np.arange(len(df_metrics2.columns)), minor=False)
ax3.set_yticks(np.arange(len(df_metrics2.index)), minor=False)
ax3.xaxis.tick_top()
ax3.grid(which="minor", c='black', ls=':', lw='0.4')
ax3.set_xticks([x-0.5 for x in range(1, len(df_metrics2.columns))], minor=True)
ax3.set_yticks([y-0.5 for y in range(1, len(df_metrics2.index))], minor=True)
wrap_labels3(df_metrics2, ax3, 5)

min_val, max_valRow = 0, 2
min_val, max_valCol = 0, number

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df_metrics[df_metrics2.columns[j]][df_metrics2.index[k]]
        t = df_metrics_tot[df_metrics_tot2.columns[j]][df_metrics_tot2.index[k]]
        ax3.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=8)
         
ax3.text(0.5, -1.3, "N° di ore con T>Tmax+2°C / N° di ore totali", ha = "center", weight = "demi")
st.pyplot(fig)


#%% Display results - TM52 compliance
st.write("Criteri di conformità con la norma TM52. Confronto tra scenari climatici.")


fig, (ax1,ax2) = plt.subplots(1,2)
fig.set_figheight(6)
fig.set_figwidth(9)

Vent = pd.DataFrame(columns=["C1", "C2", "C3"])
noVent = pd.DataFrame(columns=["C1", "C2", "C3"])

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    iniziale = comparazione

    if comparazione == "BASE":
        WFR_new = WFR_old
    else:
        WFR_new = WFR
    
    noVent.loc[iniziale, "C1"] = float(scenarios_df_compare["C1"][(scenarios_df_compare["Caso"] == comparazione)].values[0])
    noVent.loc[iniziale, "C2"] = float(scenarios_df_compare["C2"][(scenarios_df_compare["Caso"] == comparazione)].values[0])
    noVent.loc[iniziale, "C3"] = float(scenarios_df_compare["C3"][(scenarios_df_compare["Caso"] == comparazione)].values[0])

    df = pd.concat([noVent, Vent])
    # df.index = ["Zero air speed", "Increased air speed"]
    df["TOT"] = 100
    df.loc[(df["C1"] == 0) | (df["C2"] == 0) | (df["C3"] == 0), "TOT"] = 0
    df = df.astype('float64')

criteri = pd.concat([df["C1"], df["C2"], df["C3"]], axis=1)
im = ax1.matshow(criteri, cmap="RdYlGn_r",interpolation="none", aspect = 0.5)
im.norm.autoscale([0, 100])
ax1.set_xticks(np.arange(len(criteri.columns)), minor=False)
ax1.set_yticks(np.arange(len(criteri.index)), minor=False)
ax1.xaxis.tick_top()
ax1.grid(which="minor", c='black', ls=':', lw='0.4')
ax1.set_xticks([x-0.5 for x in range(1, len(criteri.columns))], minor=True)
ax1.set_yticks([y-0.5 for y in range(1, len(criteri.index))], minor=True)
wrap_labels(criteri, ax1, 5)

min_val, max_valRow = 0, 3
min_val, max_valCol = 0, number

for j in range(max_valRow):
    for k in range(max_valCol):
        c = df[criteri.columns[j]][criteri.index[k]]
        ax1.text(j, k, "{}%".format(str(round(c, 1))), va='center', ha='center', fontsize=10)

tot = pd.DataFrame(df["TOT"])
tot = tot.astype(float)    
im = ax2.matshow(tot, cmap="RdYlGn_r", interpolation="none", aspect = 0.5/3)
im.norm.autoscale([0, 100])
ax2.set_xticks(np.arange(len(tot.columns)), minor=False)
ax2.set_yticks(np.arange(len(tot.index)), minor=False)
ax2.xaxis.tick_top()
ax2.grid(which="minor", c='black', ls=':', lw='0.4')
ax2.set_xticks([x-0.5 for x in range(1, len(tot.columns))], minor=True)
ax2.set_yticks([y-0.5 for y in range(1, len(tot.index))], minor=True)
wrap_labels2(tot, ax2, 5)

truefalse(1, number, tot, ax2)

st.pyplot(fig)

# %% Calculate share of overheating days
st.write("Giorni totali di stress termico e giorni di stress termico per il periodo scolastico di spegnimento del riscaldamento. Confronto tra scenari climatici.")


heat_stress = pd.DataFrame(columns = ["Giorni di stress termico totali", "Giorni di stress termico periodo scolastico non riscaldato"], index = range(number))
heat_stress_tot = pd.DataFrame(columns = ["Giorni di stress termico totali", "Giorni di stress termico periodo scolastico non riscaldato"], index = range(number))
indice = pd.DataFrame(columns = ["caso"], index = range(number))

scenarios_df_compare["Overheating days share"] = ""
scenarios_df_compare["Overheating days share with increased air speed"] = ""

for comparazione_numero in range(number):
    comparazione = inputsRetrofit[comparazione_numero]

    iniziale = comparazione

    if comparazione == "SHGC reduction":
        SHGC_new = 0.3
        retrofit_new = retrofit
        vent_new = vent
    else:
        SHGC_new = SHGC
        if comparazione == "Walls insulation":
            retrofit_new = "WALL"
        elif comparazione == "Roof insulation":
            retrofit_new = "ROOF"
        elif comparazione == "Double glazings":
            retrofit_new = "WINDOW"
        else:
            retrofit_new = retrofit
        if comparazione == "Increase ventilation rate":
            vent_new = "8 l/s/pers"
        else:
            vent_new = vent

    if comparazione != "Increase air speed":
        temp_comparazione = pd.concat([temp_df_compare[comparazione], temp_df_compare["Tout-{}".format(city)], temp_df_compare["Tmax-{}".format(
            city)], temp_df_compare["TmaxVent-{}".format(city)], temp_df_compare["Trm-{}".format(city)]], axis=1)

        # Days in which ventilation is feasible = days in which at ALL hours the temperature outside is lower than the indoor one and lower than the threshold
        vent_comparazione = pd.DataFrame(
            0, index=temp_comparazione.index, columns=temp_comparazione.columns)

        vent_comparazione.loc[(temp_comparazione["Tout-{}".format(city)] < temp_comparazione["Tmax-{}".format(city)] - 7)
                              & (temp_comparazione["Tout-{}".format(city)] < temp_comparazione[comparazione]), comparazione] = 1

        vent_daily = vent_comparazione.resample("1440min").sum()
        temp_daily = temp_comparazione.resample("1440min").max()

        heat_comparazione = pd.DataFrame(
            0, index=temp_daily.index, columns=temp_daily.columns)
        heat_comparazione = heat_comparazione.drop(columns=["Tmax-{}".format(
            city), "TmaxVent-{}".format(city), "Tout-{}".format(city), "Trm-{}".format(city)])

        # Share of days in which indoor temperature is above the threshold and ventilation is not feasible, or in which Trm is above 30°C (limit of the adaptive chart)
        heat_comparazione.loc[((temp_daily[comparazione] > temp_daily["Tmax-{}".format(city)]) | (
            temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[comparazione] < 24), comparazione] = 1

        share = heat_comparazione.sum(axis=0) / 365 * 100

        # At least 3 consecutive days to be considered heat wave
        heat_comparazione_updated = heat_comparazione.copy()

        for day in heat_comparazione.index:
            if (day == pd.Timestamp('2025-01-01 00:00:00')) | (day == pd.Timestamp('2025-01-02 00:00:00')) | (day == pd.Timestamp('2025-12-30 00:00:00')) | (day == pd.Timestamp('2025-12-31 00:00:00')):
                ieri = 0
                laltroieri = 0
                oggi = heat_comparazione[comparazione][day]
                domani = 0
                dopodomani = 0
            else:
                laltroieri = heat_comparazione[comparazione][day -
                                                             pd.to_timedelta(2, unit='D')]
                ieri = heat_comparazione[comparazione][day -
                                                       pd.to_timedelta(1, unit='D')]
                oggi = heat_comparazione[comparazione][day]
                domani = heat_comparazione[comparazione][day +
                                                         pd.to_timedelta(1, unit='D')]
                dopodomani = heat_comparazione[comparazione][day +
                                                             pd.to_timedelta(2, unit='D')]

            if oggi == 1:
                if ((domani == 1) & (dopodomani == 1)) | ((ieri == 1) & (laltroieri == 1)) | ((ieri == 1) & (domani == 1)):
                    heat_comparazione_updated.loc[day, comparazione] = 1
                else:
                    heat_comparazione_updated.loc[day, comparazione] = 0

        share_updated = float(
            heat_comparazione_updated.sum(axis=0).values[0]) / 365 * 100
        # scenarios_df_compare["Overheating days share"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)] = float(heat_comparazione_updated.sum(axis = 0).values) / 365 * 100
        
        numeroTOT = round(heat_comparazione_updated.sum(axis=0)[comparazione])
        schoolNH_mask_daily = (heat_comparazione_updated.index >= startNH) & (heat_comparazione_updated.index < startSummer) | (heat_comparazione_updated.index > endSummer) & (heat_comparazione_updated.index < endNH)
        heat_comparazione_scuola = heat_comparazione_updated.loc[schoolNH_mask_daily].copy()
        numeroESTATE = round(heat_comparazione_scuola.sum(axis=0)[comparazione])
        
    else:
        comparazione = "BASE"
        temp_comparazione = pd.concat([temp_df_compare[comparazione], temp_df_compare["Tout-{}".format(city)], temp_df_compare["Tmax-{}".format(
            city)], temp_df_compare["TmaxVent-{}".format(city)], temp_df_compare["Trm-{}".format(city)]], axis=1)

        # Days in which ventilation is feasible = days in which at ALL hours the temperature outside is lower than the indoor one and lower than the threshold
        vent_comparazione = pd.DataFrame(
            0, index=temp_comparazione.index, columns=temp_comparazione.columns)

        vent_comparazione.loc[(temp_comparazione["Tout-{}".format(city)] < temp_comparazione["Tmax-{}".format(city)] - 7)
                              & (temp_comparazione["Tout-{}".format(city)] < temp_comparazione[comparazione]), comparazione] = 1

        vent_daily = vent_comparazione.resample("1440min").sum()
        temp_daily = temp_comparazione.resample("1440min").max()

        heat_comparazione = pd.DataFrame(
            0, index=temp_daily.index, columns=temp_daily.columns)
        heat_comparazione = heat_comparazione.drop(columns=["Tmax-{}".format(
            city), "TmaxVent-{}".format(city), "Tout-{}".format(city), "Trm-{}".format(city)])
        heat_comparazione_vent = heat_comparazione.copy()

        # Share of days in which indoor temperature is above the threshold and ventilation is not feasible, or in which Trm is above 30°C (limit of the adaptive chart)
        heat_comparazione_vent.loc[((temp_daily[comparazione] > temp_daily["TmaxVent-{}".format(city)]) | (
            temp_daily["Tout-{}".format(city)] > 30)) & (vent_daily[comparazione] < 24), comparazione] = 1

        share = heat_comparazione.sum(axis=0) / 365 * 100

        # At least 3 consecutive days to be considered heat wave
        heat_comparazione_vent_updated = heat_comparazione_vent.copy()

        for day in heat_comparazione_vent.index:
            if (day == pd.Timestamp('2025-01-01 00:00:00')) | (day == pd.Timestamp('2025-01-02 00:00:00')) | (day == pd.Timestamp('2025-12-30 00:00:00')) | (day == pd.Timestamp('2025-12-31 00:00:00')):
                ieri = 0
                laltroieri = 0
                oggi = heat_comparazione_vent[comparazione][day]
                domani = 0
                dopodomani = 0
            else:
                laltroieri = heat_comparazione_vent[comparazione][day -
                                                                  pd.to_timedelta(2, unit='D')]
                ieri = heat_comparazione_vent[comparazione][day -
                                                            pd.to_timedelta(1, unit='D')]
                oggi = heat_comparazione_vent[comparazione][day]
                domani = heat_comparazione_vent[comparazione][day +
                                                              pd.to_timedelta(1, unit='D')]
                dopodomani = heat_comparazione_vent[comparazione][day +
                                                                  pd.to_timedelta(2, unit='D')]

            if oggi == 1:
                if ((domani == 1) & (dopodomani == 1)) | ((ieri == 1) & (laltroieri == 1)) | ((ieri == 1) & (domani == 1)):
                    heat_comparazione_vent_updated.loc[day, comparazione] = 1
                else:
                    heat_comparazione_vent_updated.loc[day, comparazione] = 0

        share_updated = float(
            heat_comparazione_vent_updated.sum(axis=0).values[0]) / 365 * 100
        # scenarios_df_compare["Overheating days share with increased air speed"][(scenarios_df_compare["solar_heat_gain_coefficient"] == SHGC_new) & (scenarios_df_compare["THERMAL"] == retrofit_new) & (scenarios_df_compare["VENT"] == vent_new)] = float(heat_comparazione_vent_updated.sum(axis = 0).values) / 365 * 100
        
        numeroTOT = round(heat_comparazione_vent_updated.sum(axis=0)[comparazione])
        schoolNH_mask_daily = (heat_comparazione_vent_updated.index >= startNH) & (heat_comparazione_vent_updated.index < startSummer) | (heat_comparazione_updated.index > endSummer) & (heat_comparazione_updated.index < endNH)
        heat_comparazione_vent_scuola = heat_comparazione_vent_updated.loc[schoolNH_mask_daily].copy()
        numeroESTATE = round(heat_comparazione_vent_scuola.sum(axis=0)[comparazione])
    
    indice.loc[comparazione_numero] = [iniziale]        
    heat_stress.loc[comparazione_numero] = [numeroTOT, numeroESTATE]
    heat_stress = heat_stress.astype(float)
    heat_stress_tot.loc[comparazione_numero] = [365, heat_df_scuola.shape[0]]
    
heat_stress = heat_stress.set_index(indice["caso"])
heat_stress_tot = heat_stress_tot.set_index(indice["caso"])

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

def numeri2(max_valRow, max_valCol, df, dftot, ax):
    for j in range(max_valRow):
        for k in range(max_valCol):
            c = df[df.columns[j]][df.index[k]]
            t = dftot[dftot.columns[j]][dftot.index[k]]
            ax.text(j, k, "{} / {}".format(str(round(c)), str(round(t))), va='center', ha='center', fontsize=12)

numeri2(2, number, heat_stress, heat_stress_tot, ax)

st.pyplot(fig)

# %% Save df
# temp_df_compare.to_excel(folder + r"\PLOTS\temp.xlsx")
# dist_df_compare.to_excel(folder + r"\PLOTS\dist.xlsx")
# scenarios_df_compare.to_excel(folder + r"\PLOTS\scenarios.xlsx")
