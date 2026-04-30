# ============================================
# DASHBOARD VENDITE & PROFITTI — STREAMLIT
# ============================================
import io
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import geopandas as gpd
from adjustText import adjust_text # per le labels della Mappa

# --------------------------------------------
# LOAD & CLEAN DATA
# --------------------------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    # Convert date columns
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Ship_Date"] = pd.to_datetime(df["Ship_Date"], errors="coerce")

    # Convert numeric fields
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
    
    # Data clean for nulls and duplicates:
    df = df.drop_duplicates()
    df['Profit'] = df['Profit'].fillna(df.groupby('Sub_Category')['Profit'].transform('median'))
    df['Sales'] = df['Sales'].fillna(df.groupby('Sub_Category')['Sales'].transform('median'))

    # Feature engineering
    df["Year"] = df["Order_Date"].dt.year
    df["Month"] = df["Order_Date"].dt.month
    df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
    df["Quarter"] = df["Order_Date"].dt.quarter
    df["DayOfWeek"] = df["Order_Date"].dt.day_name()

    # KPI derivati
    df["Avg_Selling_Price"] = df["Sales"] / df["Quantity"]
    df["Ship_Delay"] = (df["Ship_Date"] - df["Order_Date"]).dt.days

    return df

# --------------------------------------------
# MAIN APP
# --------------------------------------------

st.markdown("<h1 style='text-align: center;'>Dashboard Vendite Avanzata</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Analisi completa: vendite, profitti, logistica, prodotti e mappa geografica</p>", unsafe_allow_html=True)
# Download Template Button
with open("Template_CSV_Sales.csv", "rb") as f:
    st.download_button(
        label="📥 Download Template CSV Vendite",
        data=f,
        file_name="Template_CSV_Sales.csv",
        mime="text/csv"
    )
# CSV Upload Section 
uploaded = st.file_uploader("Carica il dataset CSV", type="csv")

if uploaded is not None:
    df = load_data(uploaded)

    st.subheader("Anteprima Dataset")
    st.dataframe(df.head())

    # ========================================
    # KPI PRINCIPALI
    # ========================================
    total_profit_margin = df["Profit"].sum() / df["Sales"].sum()
    
    st.subheader("📌 KPI Principali (Performance Generale)")
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    col1.metric("Totale Vendite", f"€ {df['Sales'].sum():,.0f}")
    col2.metric("Totale Profitto", f"€ {df['Profit'].sum():,.0f}")
    col3.metric("Profit Margin Totale", f"{total_profit_margin *100:.1f}%")
    col4.metric("Ordine Medio", f"€ {df['Sales'].mean():,.0f}")
    col5.metric("Profitto medio", f"€ {df['Profit'].mean():,.0f}")
    col6.metric("Tempo Medio Spedizione", f"{df['Ship_Delay'].mean():.1f} giorni")

    # ========================================
    # ANALISI TEMPORALE — MENSILE
    # ========================================
    st.subheader("📈 Andamento Mensile Vendite")
    # Feature mensili per ogni anno
    monthly = df.groupby(["Year", "Month", "Month_Name"])[["Sales", "Profit", "Quantity"]].sum().reset_index()
    monthly = monthly.sort_values(["Year", "Month"])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly, 
                 x="Month_Name", 
                 y="Sales", 
                 hue="Year", 
                 marker="o", 
                 linewidth=2, 
                 ax=ax,
                 palette="Paired"
    )
    
    ax.set_title("Andamento Mensile delle Vendite")
    st.pyplot(fig)

    # ========================================
    # ANALISI SUB-CATEGORY — PROFIT & SALES
    # ========================================
    # Feature - Numero Vendite per Sub-Categori (descent)
    subcat = df.groupby("Sub_Category")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False).reset_index()

    # Funzione per assegnare colori in base al profit
    def color_map(profit):
        if profit < 0:
            return "#e22828"   # rosso
        elif profit < 25000:
            return "#ffee00"   # giallo
        else:
            return "#2ca02c"   # verde

    subcat["Color"] = subcat["Profit"].apply(color_map)
    
    # BARPLOTS
    # SALES PER SUB-CAT
    
    st.subheader("Sales per Sub-Category")
    
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=subcat, y="Sub_Category", 
                x="Sales", 
                ax=ax2,
                palette="YlGnBu_r" 
    )
    
    ax2.set_title("Sales per Sub-Category")
    plt.setp(ax2.get_yticklabels(), fontweight='semibold')

    st.pyplot(fig2)

    # PROFIT PER SUB-CAT
    st.subheader("Profit per Sub-Category")

    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=subcat, y="Sub_Category", 
                x="Profit", 
                ax=ax3, 
                palette=subcat["Color"].tolist()
    )
    
    ax3.set_title("Profit per Sub-Category")
    plt.setp(ax3.get_yticklabels(), fontweight='semibold')

    st.pyplot(fig3)

# ========================================
# DONUT: TOP 5 STATI CON MAGGIOR PROFITTO E MAGGIORI PERDITE
# ========================================
    st.subheader("Stati con Maggior Profitto e Maggiori Perdite")

    # Calcolo profitto totale per stato
    profit_state = df.groupby("State")["Profit"].sum().reset_index()

    # Stati con profitto positivo (Top 5)
    profit_positive = (
        profit_state[profit_state["Profit"] > 0]
        .sort_values("Profit", ascending=False)
        .head(5)
    )
    profit_positive["Perc"] = profit_positive["Profit"] / profit_positive["Profit"].sum()

    # Stati con perdite (Top 5)
    profit_negative = (
        profit_state[profit_state["Profit"] < 0]
        .sort_values("Profit", ascending=True)
        .head(5)
    )
    
    # Calcolo percentuali 
    profit_negative["Perc"] = profit_negative["Profit"].abs() / profit_negative["Profit"].abs().sum()

    # Layout affiancato
    colA, colB = st.columns(2)

    # -------------------------------
    # DONUT PROFITTI (VERDE)
    # -------------------------------
    with colA:
        fig_pos, ax_pos = plt.subplots(figsize=(6, 6))

        colors_pos = plt.cm.Greens(np.linspace(0.4, 1, len(profit_positive)))

        ax_pos.pie(
            profit_positive["Perc"],
            labels=profit_positive["State"],
            autopct="%1.1f%%",
            startangle=140,
            colors=colors_pos,
            wedgeprops={"width": 0.35},  # crea il donut
            textprops={'fontweight': 600}, # semibold
            pctdistance=0.5
        )
        
        ax_pos.set_title("Top 5 Stati con Maggior Profitto", fontweight ='semibold', pad=20)
        st.pyplot(fig_pos)

    # -------------------------------
    # DONUT PERDITE (ROSSO)
    # -------------------------------
    with colB:
        fig_neg, ax_neg = plt.subplots(figsize=(6, 6))

        colors_neg = plt.cm.Reds(np.linspace(0.4, 1, len(profit_negative)))

        ax_neg.pie(
            profit_negative["Perc"],
            labels=profit_negative["State"],
            autopct="%1.1f%%",
            startangle=140,
            colors=colors_neg,
            wedgeprops={"width": 0.35},
            textprops={'fontweight': 600}, # semibold
            pctdistance=0.5
        )

        ax_neg.set_title("Top 5 Stati con Maggiori Perdite", fontweight='semibold', pad=15)
        st.pyplot(fig_neg)

    # ========================================
    # ANALISI LOGISTICA — SHIP DELAY
    # ========================================
    st.subheader("🚚 Analisi Logistica — Tempi di Spedizione")
    # Plto giorni spedizione
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x="Ship_Delay", ax=ax4, palette="YlGnBu")
    ax4.set_title("Tempi Medi di Spedizione (giorni)")
    st.pyplot(fig4)

    # Calcolo tempi medi spedizione
    delay_region = df.groupby("State")["Ship_Delay"].mean().reset_index().sort_values("Ship_Delay", ascending=False)
    # filtro anomalie spedizioni superiori a 3gg
    delay_region = delay_region[delay_region["Ship_Delay"] > 4]
    
    st.subheader(" Ritardi Spedizione")
    # Plot ritardo spedizione in gg
    fig5, ax5 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=delay_region, y="State", x="Ship_Delay", ax=ax5, palette="Blues_r")

    ax5.set_title("Regioni con maggior riratdo (>4gg)")
    plt.setp(ax5.get_yticklabels(), fontweight= 500)

    st.pyplot(fig5)

    # ========================================
    # ANALISI GEOGRAFICA — SALES PER STATE
    # ========================================
    st.subheader("🗺️ Mappa Vendite per Stato")
    # Feature - Totale vendite per Stato 
    df_map = df.groupby("State")["Sales"].sum().reset_index()
    # Geo Dataframe - importo confini mappa degli Stati
    gdf_states = gpd.read_file("us-states.json")
    # Normalizzo nomi
    gdf_states["STATE_NAME"] = gdf_states["name"].str.strip()
    # Merge coordinate degli Stati con le features del df_map
    gdf_merged = gdf_states.merge(df_map, left_on="STATE_NAME", right_on="State", how="left")
    # Centroidi (centroids) per colori choropleth e 'States' labels
    gdf_merged["centroid"] = gdf_merged.geometry.centroid

    # Map Plot
    fig6, ax6 = plt.subplots(1, 1, figsize=(16, 12), dpi=300)
    gdf_merged.plot(
        column="Sales",
        cmap="YlGnBu",
        linewidth=0.8,
        edgecolor="0.8",
        legend=True,
        ax=ax6
    )
    # hides coordinates axis / nasconde assi coordiante
    ax6.set_axis_off()

    # --- TEXT LABELS WITH ADJUST_TEXT ---
    # Etichette/Labels degli stati sulla mappa

    # Labels Background Box 
    bbox_style = dict(facecolor="white", edgecolor="none", alpha=0.7, pad=0.4)

    texts = []
    for idx, row in gdf_merged.iterrows():
        x = row["centroid"].x
        y = row["centroid"].y

        texts.append(
            ax6.text(
                x, y,
                row["STATE_NAME"],
                fontsize=8,
                fontweight='semibold',
                ha="center",
                va="center",
                bbox=bbox_style
            )
        )

    # Adjust labels to avoid overlap
    adjust_text(
        texts,
        ax=ax6,
        arrowprops=dict(arrowstyle="-", color="gray", lw=0.5)
    )

    plt.title("Sales per State", fontweight='semibold')
    st.pyplot(fig6)

    # Download PNG Button - scaricare immagine della mappa
    buf = io.BytesIO()
    fig6.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)

    st.download_button(
        label="📥 Scarica la mappa in PNG",
        data=buf,
        file_name="sales_map.png",
        mime="image/png"
    )
