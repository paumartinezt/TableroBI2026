import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pywaffle import Waffle


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

    st.sidebar.markdown("### Configuración de Visualización")

    estaciones = ["Todas"] + sorted(df["name"].unique().tolist())
    seleccion = st.sidebar.selectbox("Selecciona una estación:", estaciones)

    nivel_slider = st.sidebar.slider("Nivel de Zoom", 1, 4, 1)
    zoom_map_dict = {
        1: 10.3,
        2: 12.0,
        3: 13.5,
        4: 15.0
    }

    tamanio_puntos = st.sidebar.slider("Tamaño de puntos en mapa", 10, 40, 18)

    columnas_status = [
        "num_bikes_available",
        "num_bikes_disabled",
        "num_docks_available",
        "num_docks_disabled"
    ]

    for col in columnas_status:
        if col not in df.columns:
            df[col] = 0

    lat_centroide = df["lat"].mean()
    lon_centroide = df["lon"].mean()

    if seleccion != "Todas":
        fila = df[df["name"] == seleccion].iloc[0]
        valores_waffle = fila[columnas_status].fillna(0).astype(int).values

        if nivel_slider == 1:
            lat_center, lon_center = lat_centroide, lon_centroide
        else:
            lat_center, lon_center = fila["lat"], fila["lon"]

        n_rows_waffle = 6
        font_waffle = 22
        leyenda_escala = "1 icono = 1 unidad"

        df["resaltado"] = df["name"].apply(
            lambda x: "Seleccionada" if x == seleccion else "Normal"
        )

    else:
        factor_escala = 100
        valores_reales = df[columnas_status].sum().fillna(0).values
        valores_waffle = (valores_reales / factor_escala).astype(int)

        lat_center, lon_center = lat_centroide, lon_centroide
        n_rows_waffle = 12
        font_waffle = 18
        leyenda_escala = f"1 icono ≈ {factor_escala} unidades"

        df["resaltado"] = "Normal"

    col_mapa, col_waffle = st.columns([2.5, 1], gap="medium")

    with col_mapa:
        st.markdown("## Ubicación de Estaciones")

        fig_map = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            size=[tamanio_puntos] * len(df),
            size_max=tamanio_puntos,
            color="resaltado",
            color_discrete_map={
                "Seleccionada": "#E74C3C",
                "Normal": "#1f77b4"
            },
            hover_name="name",
            hover_data={
                "station_id": True,
                "lat": False,
                "lon": False,
                "num_bikes_available": True,
                "num_docks_available": True,
                "resaltado": False
            },
            zoom=zoom_map_dict[nivel_slider],
            center={"lat": lat_center, "lon": lon_center},
            mapbox_style="carto-positron",
            height=650
        )

        if seleccion != "Todas":
            fig_map.add_trace(
                go.Scattermapbox(
                    lat=[fila["lat"]],
                    lon=[fila["lon"]],
                    mode="markers",
                    marker=go.scattermapbox.Marker(
                        size=tamanio_puntos + 15,
                        color="red",
                        symbol="marker"
                    ),
                    showlegend=False,
                    hoverinfo="skip"
                )
            )

        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            showlegend=False
        )

        st.plotly_chart(fig_map, use_container_width=True)

    with col_waffle:
        titulo_waffle = seleccion if seleccion != "Todas" else "CDMX"
        st.markdown(f"## Disponibilidad: {titulo_waffle}")

        if int(sum(valores_waffle)) > 0:
            fig_waffle = plt.figure(
                FigureClass=Waffle,
                rows=n_rows_waffle,
                values=valores_waffle,
                colors=["#2ecc71", "#e74c3c", "#3498db", "#f39c12"],
                icons="bicycle",
                font_size=font_waffle,
                figsize=(7, 8),
                legend={
                    "labels": [
                        "Bici disponible",
                        "Bici dañada",
                        "Puerto libre",
                        "Puerto dañado"
                    ],
                    "loc": "lower center",
                    "bbox_to_anchor": (0.5, -0.15),
                    "ncol": 2,
                    "fontsize": 10,
                    "frameon": False
                }
            )

            plt.subplots_adjust(left=0.08, right=0.92, top=0.95, bottom=0.18)

            st.pyplot(fig_waffle, use_container_width=True, clear_figure=True)
            st.caption(f"**Escala:** {leyenda_escala}")
        else:
            st.info("No hay datos suficientes para generar el gráfico de disponibilidad.")

    if seleccion != "Todas":
        st.markdown("### Información de la estación seleccionada")
        a, b = st.columns(2)

        with a:
            st.write(f"**ID:** {fila['station_id']}")
            st.write(f"**Nombre:** {fila['name']}")
            if "capacity" in fila.index:
                st.write(f"**Capacidad:** {fila['capacity']}")

        with b:
            st.write(f"**Latitud:** {fila['lat']}")
            st.write(f"**Longitud:** {fila['lon']}")
            st.write(f"**Bicis disponibles:** {fila['num_bikes_available']}")
            st.write(f"**Bicis dañadas:** {fila['num_bikes_disabled']}")
            st.write(f"**Puertos disponibles:** {fila['num_docks_available']}")
            st.write(f"**Puertos dañados:** {fila['num_docks_disabled']}")
