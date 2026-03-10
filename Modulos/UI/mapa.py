import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def clasificar_estacion(row):
    bikes = row["num_bikes_available"] if "num_bikes_available" in row.index else None
    docks = row["num_docks_available"] if "num_docks_available" in row.index else None

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

    # Crear estado visual
    if "num_bikes_available" in df.columns and "num_docks_available" in df.columns:
        df["estado_estacion"] = df.apply(clasificar_estacion, axis=1)
    else:
        df["estado_estacion"] = "Sin clasificar"

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
        punto = df[df["name"] == seleccion].iloc[0]

        if nivel_zoom == 1:
            lat_center, lon_center = lat_centroide, lon_centroide
        else:
            lat_center, lon_center = punto["lat"], punto["lon"]

        zoom_val = zoom_map[nivel_zoom]
    else:
        lat_center, lon_center = lat_centroide, lon_centroide
        zoom_val = zoom_map[1]

    color_map = {
        "Bicis disponibles": "#2E8B57",
        "Puertos disponibles": "#1F77B4",
        "Sin bicicletas": "#D62728",
        "Sin puertos": "#F4A300",
        "Sin clasificar": "#BDBDBD"
    }

    # Texto hover manual para que sí salga todo
    df["hover_texto"] = (
        "<b>" + df["name"].astype(str) + "</b><br>" +
        "ID: " + df["station_id"].astype(str) + "<br>" +
        "Estado: " + df["estado_estacion"].astype(str) + "<br>" +
        ("Capacidad: " + df["capacity"].astype(str) + "<br>" if "capacity" in df.columns else "") +
        ("Bicis disponibles: " + df["num_bikes_available"].astype(str) + "<br>" if "num_bikes_available" in df.columns else "") +
        ("Puertos disponibles: " + df["num_docks_available"].astype(str) if "num_docks_available" in df.columns else "")
    )

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="estado_estacion",
        color_discrete_map=color_map,
        zoom=zoom_val,
        center={"lat": lat_center, "lon": lon_center},
        height=650
    )

    fig.update_traces(
        marker=dict(size=13, opacity=0.70),
        hovertemplate="%{customdata[0]}<extra></extra>",
        customdata=df[["hover_texto"]].values
    )

    if punto is not None:
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

        hover_punto = (
            f"<b>{punto['name']}</b><br>"
            f"ID: {punto['station_id']}<br>"
            f"Estado: {punto['estado_estacion']}<br>"
            f"Capacidad: {punto['capacity']}<br>" if "capacity" in punto.index else
            f"<b>{punto['name']}</b><br>ID: {punto['station_id']}<br>Estado: {punto['estado_estacion']}<br>"
        )

        if "num_bikes_available" in punto.index:
            hover_punto += f"Bicis disponibles: {punto['num_bikes_available']}<br>"
        if "num_docks_available" in punto.index:
            hover_punto += f"Puertos disponibles: {punto['num_docks_available']}"

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
                hovertemplate=hover_punto + "<extra></extra>",
                name="Estación seleccionada",
                showlegend=True
            )
        )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        showlegend=True,
        legend_title_text="Estado de la estación",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    if punto is not None:
        st.markdown("### Información de la estación seleccionada")
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**ID:** {punto['station_id']}")
            st.write(f"**Nombre:** {punto['name']}")
            if "capacity" in punto.index:
                st.write(f"**Capacidad:** {punto['capacity']}")

        with col2:
            st.write(f"**Latitud:** {punto['lat']}")
            st.write(f"**Longitud:** {punto['lon']}")
            if "num_bikes_available" in punto.index:
                st.write(f"**Bicis disponibles:** {punto['num_bikes_available']}")
            if "num_docks_available" in punto.index:
                st.write(f"**Puertos disponibles:** {punto['num_docks_available']}")
