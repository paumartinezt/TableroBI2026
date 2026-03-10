import streamlit as st

st.set_page_config(
    page_title="Análisis de Movilidad: Ecobici CDMX",
    layout="wide",
    initial_sidebar_state="expanded"
)

from Modulos.UI.header import show_header
from Modulos.data.Ecobiciservice import cargar_estaciones
from Modulos.UI.mapa import show_mapa_estaciones


show_header("Mi primera GUI en Streamlit")

df = cargar_estaciones()

show_mapa_estaciones(df)
