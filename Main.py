# Sección de importación de módulos
from Modulos.UI.header import show_header

# Sección para crear la GUI
show_header("Mi primera GUI en Streamlit")

from Modulos.data.Ecobiciservice import cargar_estaciones
from Modulos.UI.mapa import show_mapa_estaciones

df = cargar_estaciones()

show_mapa_estaciones(df)
