from Modulos.UI.header import show_header
from Modulos.data.Ecobiciservice import cargar_estaciones
from Modulos.UI.mapa import EcobiciViz

show_header("Mi primera GUI en Streamlit")

df = cargar_estaciones()

viz = EcobiciViz()
viz.render_map(df)
