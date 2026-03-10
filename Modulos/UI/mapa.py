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
        return "Alta disponibilidad"
    else:
        return "Puertos disponibles"


def render_bike_icons(
    bicis_disponibles,
    bicis_danadas=0,
    puertos_disponibles=0,
    puertos_danados=0,
    scale=100
):
    st.markdown("### Disponibilidad: CDMX")

    verdes = int(bicis_disponibles / scale) if bicis_disponibles > 0 else 0
    rojas = int(bicis_danadas / scale) if bicis_danadas > 0 else 0
    azules = int(puertos_disponibles / scale) if puertos_disponibles > 0 else 0
    naranjas = int(puertos_danados / scale) if puertos_danados > 0 else 0

    icons = []
    colors = []

    icons += ["🚲"] * verdes
    colors += ["#49A96E"] * verdes

    icons += ["🚲"] * rojas
    colors += ["#E45757"] * rojas

    icons += ["🚲"] * azules
    colors += ["#4A90E2"] * azules

    icons += ["🚲"] * naranjas
    colors += ["#F5A623"] * naranjas

    if len(icons) == 0:
        st.write("Sin datos de disponibilidad")
        return

    x = []
    y = []

    columnas = 10
    for i in range(len(icons)):
        x.append(i % columnas)
        y.append(-(i // columnas))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="text",
            text=icons,
            textfont=dict(
                size=24,
                color=colors
            ),
            hoverinfo="skip",
            showlegend=False
        )
    )

    fig.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        <div style="font-size:14px; line-height:1.8;">
            <span style="color:#49A96E;">🚲</span> Bici disponible<br>
            <span style="color:#E45757;">🚲</span> Bici dañada<br>
            <span style="color:#4A90E2;">🚲</span> Puerto disponible<br>
            <span style="color:#F5A623;">🚲</span> Puerto dañado<br><br>
            <span style="color:gray;">Escala: 1 bici ≈ 100 unidades</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_mapa_estaciones(df: pd.DataFrame):
    columnas_necesarias = ["name", "lat", "lon", "station_id"]
    for col in columnas_necesarias:
        if col not in df.columns:
            st.error(f"Falta la columna: {col}")
            return

    df = df.copy()
    df = df.dropna(subset=["name", "lat", "lon", "station_id"])

    if "num_bikes_available" in df.columns and "num_docks_available" in df.columns:
        df["estado_estacion"] = df.apply(clasificar_estacion, axis=1)
    else:
        df["estado_estacion"] = "Sin clasificar"

    # SIDEBAR
    st.sidebar.markdown("## Configuración de Visualización")

    estaciones = ["Todas"] + sorted(df["name"].unique().tolist())
    seleccion = st.sidebar.selectbox(
        "Selecciona una estación:",
        estaciones
    )

    nivel_zoom = st.sidebar.slider(
        "Nivel de Zoom",
        min_value=1,
        max_value=4,
        value=1
    )

    tamanio_puntos = st.sidebar.slider(
        "Tamaño de puntos en mapa",
        min_value=8,
        max_value=24,
        value=14
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
        "Alta disponibilidad": "#5DBB63",
        "Puertos disponibles": "#5DADE2",
        "Sin bicicletas": "#E74C3C",
        "Sin puertos": "#F5B041",
        "Sin clasificar": "#BDBDBD"
    }

    df["hover_texto"] = (
        "<b>" + df["name"].astype(str) + "</b><br>" +
        "ID: " + df["station_id"].astype(str) + "<br>" +
        "Estado: " + df["estado_estacion"].astype(str) + "<br>" +
        ("Capacidad: " + df["capacity"].astype(str) + "<br>" if "capacity" in df.columns else "") +
        ("Bicis disponibles: " + df["num_bikes_available"].astype(str) + "<br>" if "num_bikes_available" in df.columns else "") +
        ("Puertos disponibles: " + df["num_docks_available"].astype(str) if "num_docks_available" in df.columns else "")
    )

    col1, col2 = st.columns([3, 1.2])

    with col1:
        st.markdown("## Ubicación de Estaciones")

        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            color="estado_estacion",
            color_discrete_map=color_map,
            zoom=zoom_val,
            center={"lat": lat_center, "lon": lon_center},
            height=800
        )

        fig.update_traces(
            marker=dict(size=tamanio_puntos, opacity=0.58),
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
                        size=tamanio_puntos + 14,
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
                        size=tamanio_puntos + 4,
                        color="#2E4053",
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
            showlegend=True,
            legend_title_text="Estado de la estación",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.01,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        total_bikes = int(df["num_bikes_available"].sum()) if "num_bikes_available" in df.columns else 0
        total_disabled = int(df["num_bikes_disabled"].sum()) if "num_bikes_disabled" in df.columns else 0
        total_docks = int(df["num_docks_available"].sum()) if "num_docks_available" in df.columns else 0
        total_docks_disabled = int(df["num_docks_disabled"].sum()) if "num_docks_disabled" in df.columns else 0

        render_bike_icons(
            bicis_disponibles=total_bikes,
            bicis_danadas=total_disabled,
            puertos_disponibles=total_docks,
            puertos_danados=total_docks_disabled,
            scale=100
        )

    if punto is not None:
        st.markdown("### Información de la estación seleccionada")
        a, b = st.columns(2)

        with a:
            st.write(f"**ID:** {punto['station_id']}")
            st.write(f"**Nombre:** {punto['name']}")
            if "capacity" in punto.index:
                st.write(f"**Capacidad:** {punto['capacity']}")

        with b:
            st.write(f"**Latitud:** {punto['lat']}")
            st.write(f"**Longitud:** {punto['lon']}")
            if "num_bikes_available" in punto.index:
                st.write(f"**Bicis disponibles:** {punto['num_bikes_available']}")
            if "num_docks_available" in punto.index:
                st.write(f"**Puertos disponibles:** {punto['num_docks_available']}")
