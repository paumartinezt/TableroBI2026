import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def clasificar_estacion(row):
    bikes = row["num_bikes_available"] if "num_bikes_available" in row else None
    docks = row["num_docks_available"] if "num_docks_available" in row else None

    if bikes is None or docks is None:
        return "Sin clasificar"

    if bikes == 0:
        return "Sin bicicletas"
    elif docks == 0:
        return "Sin puertos"
    elif bikes >= docks:
        return "Bicis disponibles"
    else:
        return "Puertos disponibles"


def show_mapa_estaciones(df: pd.DataFrame):
    st.subheader("Mapa de Estaciones Ecobici")

    columnas_necesarias = ["name", "lat", "lon", "station_id"]
    for col in columnas_necesarias:
        if col not in df.columns:
            st.error(f"Falta la columna: {col}")
            return

    df = df.copy()
    df = df.dropna(subset=["name", "lat", "lon", "station_id"])

    # Clasificación visual de estaciones
    if "num_bikes_available" in df.columns and "num_docks_available" in df.columns:
        df["estado_estacion"] = df.apply(clasificar_estacion, axis=1)
    else:
        df["estado_estacion"] = "Sin clasificar"

    # Selector de estación
    estaciones = ["Todas"] + sorted(df["name"].unique().tolist())
    seleccion = st.selectbox(
        "Busca y selecciona una estación para resaltarla:",
        estaciones
    )

    # Slider de zoom
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

    # Centroide general
    lat_centroide = df["lat"].mean()
    lon_centroide = df["lon"].mean()

    punto = None

    if seleccion != "Todas":
        punto = df[df["name"] == seleccion].iloc[0]

        # Nivel 1 = vista general, no zoom automático
        if nivel_zoom == 1:
            lat_center, lon_center = lat_centroide, lon_centroide
        else:
            lat_center, lon_center = punto["lat"], punto["lon"]

        zoom_val = zoom_map[nivel_zoom]
    else:
        lat_center, lon_center = lat_centroide, lon_centroide
        zoom_val = zoom_map[1]

    # Colores por estado
    color_map = {
        "Bicis disponibles": "#2E8B57",     # verde
        "Puertos disponibles": "#1F77B4",   # azul
        "Sin bicicletas": "#D62728",        # rojo
        "Sin puertos": "#F4A300",           # naranja
        "Sin clasificar": "#BDBDBD"         # gris
    }

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
            "num_bikes_available": "num_bikes_available" in df.columns,
            "num_docks_available": "num_docks_available" in df.columns,
            "estado_estacion": True
        },
        color="estado_estacion",
        color_discrete_map=color_map,
        zoom=zoom_val,
        center={"lat": lat_center, "lon": lon_center},
        height=650
    )

    # Tamaño de los puntos base
    fig.update_traces(
        marker=dict(
            size=13,
            opacity=0.70
        )
    )

    # Marcador extra para estación seleccionada
    if punto is not None:
        # halo exterior
        fig.add_trace(
            go.Scattermapbox(
                lat=[punto["lat"]],
                lon=[punto["lon"]],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=30,
                    color="white",
                    opacity=0.95
                ),
                hoverinfo="skip",
                showlegend=False
            )
        )

        # marcador principal
        fig.add_trace(
            go.Scattermapbox(
                lat=[punto["lat"]],
                lon=[punto["lon"]],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=20,
                    color="#5C4033",
                    opacity=1.0
                ),
                text=[punto["name"]],
                customdata=[[punto["station_id"]]],
                hovertemplate="<b>%{text}</b><br>ID: %{customdata[0]}<extra></extra>",
                name="Estación seleccionada",
                showlegend=True
            )
        )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend_title_text="Estado de la estación"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Información de estación seleccionada
    if punto is not None:
        st.markdown("### Información de la estación seleccionada")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**ID:** {punto['station_id']}")
            st.write(f"**Nombre:** {punto['name']}")
            if "capacity" in df.columns:
                st.write(f"**Capacidad:** {punto['capacity']}")

        with col2:
            st.write(f"**Latitud:** {punto['lat']}")
            st.write(f"**Longitud:** {punto['lon']}")
            if "num_bikes_available" in df.columns:
                st.write(f"**Bicis disponibles:** {punto['num_bikes_available']}")
            if "num_docks_available" in df.columns:
                st.write(f"**Puertos disponibles:** {punto['num_docks_available']}")
