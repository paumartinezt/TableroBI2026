# Sección de importación de módulos
from Modulos.UI.header import show_header

# Sección para crear la GUI
show_header("Mi primera GUI en Streamlit")

from Modulos.data.Ecobiciservice import cargar_estaciones
import streamlit as st

df = cargar_estaciones()

st.write(df.head())
