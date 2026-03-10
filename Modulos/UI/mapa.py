import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def show_mapa_estaciones(df: pd.DataFrame):
    st.subheader("Mapa de estaciones Ecobici en CDMX")
    st.caption("Versión con slider")

    columnas_necesarias = ["station_id", "name", "lat", "lon"]
    for col in columnas_necesarias:
        if col not in df.columns:
            st.error(f"Falta la columna: {col}")
            return

    df_mapa = df.copy().dropna(subset=["station_id", "name", "lat", "lon"])
    df_mapa["opcion"] = df_mapa["station_id"].astype(str) + " - " + df_mapa["name"]

    opciones = ["Ninguna"] + sorted(df_mapa["opcion"].unique().tolist())

    estacion_seleccionada = st.selectbox(
        "Selecciona una estación",
        options=opciones,
        index=0
    )

    nivel_zoom = st.slider("Acercamiento del mapa", 1, 4, 1)

    zoom_map = {
        1: 10.3,
        2: 12.0,
        3: 13.5,
        4: 15.0
    }

    centroide_lat = df_mapa["lat"].mean()
    centroide_lon = df_mapa["lon"].mean()

    estacion_info = None

    if estacion_seleccionada == "Ninguna":
        centro_lat = centroide_lat
        centro_lon = centroide_lon
        zoom_actual = zoom_map[1]
    else:
        estacion_info = df_mapa[df_mapa["opcion"] == estacion_seleccionada].iloc[0]

        if nivel_zoom == 1:
            centro_lat = centroide_lat
            centro_lon = centroide_lon
        else:
            centro_lat = estacion_info["lat"]
            centro_lon = estacion_info["lon"]

        zoom_actual = zoom_map[nivel_zoom]

    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lat=df_mapa["lat"],
            lon=df_mapa["lon"],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=9,
                color="#CBB89D",
                opacity=0.45
            ),
            text=df_mapa["name"],
            customdata=df_mapa[["station_id"]],
            hovertemplate="<b>%{text}</b><br>ID: %{customdata[0]}<extra></extra>",
            name="Otras estaciones"
        )
    )

    if estacion_info is not None:
        fig.add_trace(
            go.Scattermapbox(
                lat=[estacion_info["lat"]],
                lon=[estacion_info["lon"]],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=24,
                    color="#9C5B2E",
                    opacity=1.0
                ),
                text=[estacion_info["name"]],
                customdata=[[estacion_info["station_id"]]],
                hovertemplate="<b>%{text}</b><br>ID: %{customdata[0]}<extra></extra>",
                name="Estación seleccionada"
            )
        )

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center={"lat": centro_lat, "lon": centro_lon},
            zoom=zoom_actual
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)

    if estacion_info is not None:
        st.markdown("### Información de la estación seleccionada")
        st.write(f"**ID:** {estacion_info['station_id']}")
        st.write(f"**Nombre:** {estacion_info['name']}")
        st.write(f"**Latitud:** {estacion_info['lat']}")
        st.write(f"**Longitud:** {estacion_info['lon']}")
