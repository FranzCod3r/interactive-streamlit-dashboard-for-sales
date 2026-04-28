import io
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import geopandas as gpd


df = pd.read_csv("Template_CSV_Sales.csv")

print(df.isnull().sum())

df.info()

# Conta quanti valori nulli di Profit ci sono per ogni Sub_Category
null_distribution = df[df['Profit'].isnull()].groupby('Sub_Category').size()

print(null_distribution)

# Percentuale di nulli sul totale di ogni categoria
total_per_cat = df.groupby('Sub_Category').size()
nulls_per_cat = df[df['Profit'].isnull()].groupby('Sub_Category').size()

pct_nulls = (nulls_per_cat / total_per_cat) * 100
print(pct_nulls.sort_values(ascending=False))

# Calcoliamo la mediana del Profit per ogni sottocategoria
# Usiamo transform per 'spalmare' le mediane su tutte le righe originali
df['Profit'] = df['Profit'].fillna(df.groupby('Sub_Category')['Profit'].transform('median'))

# Verifica se sono rimasti nulli
print(f"Nulli residui in Profit: {df['Profit'].isnull().sum()}")


# Applichiamo la mediana della sottocategoria per riempire i nulli in Sales
df['Sales'] = df['Sales'].fillna(df.groupby('Sub_Category')['Sales'].transform('median'))

# Verifica finale per tutte le colonne numeriche
print(df[['Sales', 'Quantity', 'Profit']].isnull().sum())



print(df.isnull().sum())

df.info()



