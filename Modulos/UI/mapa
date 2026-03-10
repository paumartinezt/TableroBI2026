import streamlit as st
import plotly.express as px
import pandas as pd


def show_mapa_estaciones(df: pd.DataFrame):
    st.subheader("Mapa de estaciones Ecobici en CDMX")

    # Validación básica
    columnas_necesarias = ["station_id", "name", "lat", "lon"]
    for col in columnas_necesarias:
        if col not in df.columns:
            st.error(f"Falta la columna: {col}")
            return

    # Copia para no modificar el dataframe original
    df_mapa = df.copy()

    # Lista desplegable
    estacion_seleccionada = st.selectbox(
        "Selecciona una estación",
        options=df_mapa["name"].sort_values().unique()
    )

    # Crear columna para colorear
    df_mapa["tipo"] = df_mapa["name"].apply(
        lambda x: "Estación seleccionada" if x == estacion_seleccionada else "Otras estaciones"
    )

    # Crear mapa
    fig = px.scatter_mapbox(
        df_mapa,
        lat="lat",
        lon="lon",
        hover_name="name",
        hover_data={
            "station_id": True,
            "lat": False,
            "lon": False,
            "tipo": False
        },
        color="tipo",
        color_discrete_map={
            "Otras estaciones": "blue",
            "Estación seleccionada": "red"
        },
        zoom=10.5,
        height=600
    )

    # Estilo del mapa sin token
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    # Centrar el mapa en CDMX
    fig.update_layout(
        mapbox_center={
            "lat": df_mapa["lat"].mean(),
            "lon": df_mapa["lon"].mean()
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    # Mostrar datos de la estación seleccionada
    estacion_info = df_mapa[df_mapa["name"] == estacion_seleccionada].iloc[0]

    st.write("### Información de la estación seleccionada")
    st.write(f"**ID:** {estacion_info['station_id']}")
    st.write(f"**Nombre:** {estacion_info['name']}")
    st.write(f"**Latitud:** {estacion_info['lat']}")
    st.write(f"**Longitud:** {estacion_info['lon']}")
