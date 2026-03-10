import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def show_mapa_estaciones(df: pd.DataFrame):
    st.subheader("Mapa de Estaciones Ecobici")

    columnas_necesarias = ["name", "lat", "lon", "station_id"]
    for col in columnas_necesarias:
        if col not in df.columns:
            st.error(f"Falta la columna: {col}")
            return

    df = df.copy()
    df = df.dropna(subset=["name", "lat", "lon", "station_id"])

    estaciones = ["Todas"] + sorted(df["name"].unique().tolist())
    seleccion = st.selectbox(
        "Busca y selecciona una estación para resaltarla:",
        estaciones
    )

    nivel_zoom = st.slider(
        "Nivel de zoom",
        min_value=1,
        max_value=4,
        value=1
    )

    zoom_map = {
        1: 10.3,
        2: 12.0,
        3: 13.5,
        4: 15.0
    }

    lat_centroide = df["lat"].mean()
    lon_centroide = df["lon"].mean()

    punto = None

    if seleccion != "Todas":
        df["resaltado"] = df["name"].apply(
            lambda x: "Seleccionada" if x == seleccion else "Normal"
        )

        color_map = {
            "Seleccionada": "#A06A42",
            "Normal": "#CFC3B3"
        }

        punto = df[df["name"] == seleccion].iloc[0]

        if nivel_zoom == 1:
            lat_center, lon_center = lat_centroide, lon_centroide
        else:
            lat_center, lon_center = punto["lat"], punto["lon"]

        zoom_val = zoom_map[nivel_zoom]

    else:
        df["resaltado"] = "Normal"
        color_map = {"Normal": "#CFC3B3"}
        lat_center, lon_center = lat_centroide, lon_centroide
        zoom_val = zoom_map[1]

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        hover_name="name",
        hover_data={
            "lat": False,
            "lon": False,
            "station_id": True,
            "capacity": "capacity" in df.columns,
            "num_bikes_available": "num_bikes_available" in df.columns
        },
        color="resaltado",
        color_discrete_map=color_map,
        zoom=zoom_val,
        center={"lat": lat_center, "lon": lon_center},
        height=650
    )

    fig.update_traces(
        marker=dict(
            size=11,
            opacity=0.55
        )
    )

    if punto is not None:
        fig.add_trace(
            go.Scattermapbox(
                lat=[punto["lat"]],
                lon=[punto["lon"]],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=28,
                    color="white",
                    opacity=0.95
                ),
                hoverinfo="skip",
                showlegend=False
            )
        )

        fig.add_trace(
            go.Scattermapbox(
                lat=[punto["lat"]],
                lon=[punto["lon"]],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=18,
                    color="#8B5E3C",
                    opacity=1.0
                ),
                text=[punto["name"]],
                customdata=[[punto["station_id"]]],
                hovertemplate="<b>%{text}</b><br>ID: %{customdata[0]}<extra></extra>",
                name="Estación seleccionada",
                showlegend=False
            )
        )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
