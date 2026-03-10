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

    # Copia limpia
    df_mapa = df.copy()

    # Eliminar nulos por seguridad
    df_mapa = df_mapa.dropna(subset=["lat", "lon", "name", "station_id"])

    # Crear opción visual para selectbox
    df_mapa["opcion"] = df_mapa["station_id"].astype(str) + " - " + df_mapa["name"]

    opciones = ["Ninguna"] + sorted(df_mapa["opcion"].unique().tolist())

    estacion_seleccionada = st.selectbox(
        "Selecciona una estación",
        options=opciones,
        index=0
    )

    # Slider de zoom
    nivel_zoom = st.slider(
        "Nivel de zoom",
        min_value=1,
        max_value=4,
        value=1,
        help="Nivel 1 muestra una vista general y el nivel 4 acerca el mapa a la estación seleccionada."
    )

    # Mapeo de niveles a zoom de Plotly
    zoom_map = {
        1: 10.4,
        2: 11.8,
        3: 13.2,
        4: 14.8
    }

    # Centroide general
    centroide_lat = df_mapa["lat"].mean()
    centroide_lon = df_mapa["lon"].mean()

    # Caso 1: no hay estación seleccionada
    if estacion_seleccionada == "Ninguna":
        centro_lat = centroide_lat
        centro_lon = centroide_lon
        zoom_actual = zoom_map[1]
        df_mapa["tipo"] = "Estaciones"

        fig = px.scatter_mapbox(
            df_mapa,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data={
                "station_id": True,
                "lat": False,
                "lon": False,
                "tipo": False,
                "opcion": False
            },
            color="tipo",
            color_discrete_map={
                "Estaciones": "#B8A27A"
            },
            zoom=zoom_actual,
            height=650
        )

        fig.update_traces(
            marker=dict(size=9, opacity=0.72)
        )

    # Caso 2: sí hay estación seleccionada
    else:
        estacion_info = df_mapa[df_mapa["opcion"] == estacion_seleccionada].iloc[0]

        centro_lat = estacion_info["lat"] if nivel_zoom > 1 else centroide_lat
        centro_lon = estacion_info["lon"] if nivel_zoom > 1 else centroide_lon
        zoom_actual = zoom_map[nivel_zoom]

        df_mapa["tipo"] = df_mapa["opcion"].apply(
            lambda x: "Estación seleccionada" if x == estacion_seleccionada else "Otras estaciones"
        )

        fig = px.scatter_mapbox(
            df_mapa,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data={
                "station_id": True,
                "lat": False,
                "lon": False,
                "tipo": False,
                "opcion": False
            },
            color="tipo",
            color_discrete_map={
                "Otras estaciones": "#CFC5B3",
                "Estación seleccionada": "#8C5E3C"
            },
            zoom=zoom_actual,
            height=650
        )

        # Hacer la seleccionada más visible
        tamaños = [
            16 if tipo == "Estación seleccionada" else 8
            for tipo in df_mapa["tipo"]
        ]
        opacidades = [
            0.95 if tipo == "Estación seleccionada" else 0.45
            for tipo in df_mapa["tipo"]
        ]

        fig.update_traces(
            marker=dict(size=tamaños, opacity=opacidades)
        )

    # Estilo más aesthetic
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": centro_lat, "lon": centro_lon},
        margin={"r": 0, "t": 10, "l": 0, "b": 0},
        legend_title_text="",
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Info de la estación
    if estacion_seleccionada != "Ninguna":
        estacion_info = df_mapa[df_mapa["opcion"] == estacion_seleccionada].iloc[0]

        st.markdown("### Información de la estación seleccionada")
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**ID:** {estacion_info['station_id']}")
            st.write(f"**Nombre:** {estacion_info['name']}")

        with col2:
            st.write(f"**Latitud:** {estacion_info['lat']}")
            st.write(f"**Longitud:** {estacion_info['lon']}")
