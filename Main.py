from Modulos.UI.header import show_header
import streamlit as st
from Modulos.data.Ecobiciservice import cargar_estaciones
from Modulos.UI.mapa import show_mapa_estaciones

show_header("Mi primera GUI en Streamlit")
st.write("PRUEBA NUEVA 9:24 PM")

df = cargar_estaciones()
show_mapa_estaciones(df)
