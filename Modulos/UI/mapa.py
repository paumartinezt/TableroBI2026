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


def show_section_card(title, items):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        for label, value in items:
            st.caption(label)
            st.write(value)


def show_mapa_estaciones(df: pd.DataFrame):
    columnas_necesarias = ["name", "lat", "lon", "station_id"]
    for col in columnas_necesarias:
        if col not in df.columns:
            st.error(f"Falta la columna: {col}")
            return

    df = df.copy()
    df = df.dropna(subset=["name", "lat", "lon", "station_id"])

    columnas_status = [
        "num_bikes_available",
        "num_bikes_disabled",
        "num_docks_available",
        "num_docks_disabled"
    ]
    for col in columnas_status:
        if col not in df.columns:
            df[col] = 0

    df["estado_estacion"] = df.apply(clasificar_estacion, axis=1)

    # =========================
    # SIDEBAR
    # =========================
    st.sidebar.markdown("## Configuración de Visualización")

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

    estados_disponibles = sorted(df["estado_estacion"].unique().tolist())
    filtro_estados = st.sidebar.multiselect(
        "Filtrar por estado:",
        options=estados_disponibles,
        default=estados_disponibles
    )

    # =========================
    # DATAFRAME ORIGINAL Y FILTRO
    # =========================
    df_original = df.copy()

    fila = None
    if seleccion != "Todas" and seleccion in df_original["name"].values:
        fila = df_original[df_original["name"] == seleccion].iloc[0]

    df = df_original[df_original["estado_estacion"].isin(filtro_estados)].copy()

    # Si la estación seleccionada no quedó en el filtro, la volvemos a agregar
    if fila is not None and fila["name"] not in df["name"].values:
        df = pd.concat([df, fila.to_frame().T], ignore_index=True)
        st.info("La estación seleccionada quedó fuera del filtro de estado, pero se mantiene visible como referencia.")

    if df.empty:
        st.warning("No hay datos disponibles con los filtros seleccionados.")
        return

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

    lat_centroide = df["lat"].mean()
    lon_centroide = df["lon"].mean()

    # =========================
    # LÓGICA DE SELECCIÓN Y WAFFLE
    # =========================
    if seleccion != "Todas" and fila is not None:
        valores_waffle = fila[columnas_status].fillna(0).astype(int).values

        if nivel_slider == 1:
            lat_center, lon_center = lat_centroide, lon_centroide
        else:
            lat_center, lon_center = float(fila["lat"]), float(fila["lon"])

        n_rows_waffle = 6
        font_waffle = 20
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
        seleccion = "Todas"

    # =========================
    # KPIs
    # =========================
    total_estaciones = df["station_id"].nunique()
    total_bikes = int(df["num_bikes_available"].sum())
    total_docks = int(df["num_docks_available"].sum())
    estaciones_sin_bicis = int((df["num_bikes_available"] == 0).sum())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Estaciones visibles", total_estaciones)
    with k2:
        st.metric("Bicis disponibles", total_bikes)
    with k3:
        st.metric("Puertos disponibles", total_docks)
    with k4:
        st.metric("Estaciones sin bicis", estaciones_sin_bicis)

    # =========================
    # HOVER DEL MAPA
    # =========================
    df["hover_texto"] = (
        "<b>" + df["name"].astype(str) + "</b><br>"
        + "ID: " + df["station_id"].astype(str) + "<br>"
        + "Estado: " + df["estado_estacion"].astype(str) + "<br>"
        + "Bicis disponibles: " + df["num_bikes_available"].astype(str) + "<br>"
        + "Bicis dañadas: " + df["num_bikes_disabled"].astype(str) + "<br>"
        + "Puertos disponibles: " + df["num_docks_available"].astype(str) + "<br>"
        + "Puertos dañados: " + df["num_docks_disabled"].astype(str)
    )

    # =========================
    # LAYOUT PRINCIPAL
    # =========================
    col_mapa, col_waffle = st.columns([2.4, 1], gap="large")

    with col_mapa:
        st.markdown("## Ubicación de Estaciones")

        fig_map = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            color="resaltado",
            color_discrete_map={
                "Seleccionada": "#e63946",
                "Normal": "#3b82f6"
            },
            hover_name="name",
            zoom=zoom_map_dict[nivel_slider],
            center={"lat": lat_center, "lon": lon_center},
            mapbox_style="carto-positron",
            height=680
        )

        fig_map.update_traces(
            marker=dict(size=tamanio_puntos, opacity=0.58),
            hovertemplate="%{customdata[0]}<extra></extra>",
            customdata=df[["hover_texto"]].values
        )

        if seleccion != "Todas" and fila is not None:
            fig_map.add_trace(
                go.Scattermapbox(
                    lat=[float(fila["lat"])],
                    lon=[float(fila["lon"])],
                    mode="markers",
                    marker=go.scattermapbox.Marker(
                        size=tamanio_puntos + 15,
                        color="#e63946",
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

            plt.subplots_adjust(left=0.08, right=0.92, top=0.95, bottom=0.20)
            st.pyplot(fig_waffle, use_container_width=True, clear_figure=True)
            st.caption(f"**Escala:** {leyenda_escala}")
        else:
            st.info("No hay datos suficientes para generar el gráfico de disponibilidad.")

    # =========================
    # INFORMACIÓN DE ESTACIÓN
    # =========================
    if seleccion != "Todas" and fila is not None:
        st.markdown("## Información de la estación seleccionada")

        c1, c2 = st.columns(2)

        with c1:
            show_section_card(
                "Datos generales",
                [
                    ("ID", fila["station_id"]),
                    ("Nombre", fila["name"]),
                    ("Capacidad", fila["capacity"] if "capacity" in fila.index else "N/D"),
                ]
            )

        with c2:
            show_section_card(
                "Estado operativo",
                [
                    ("Latitud", fila["lat"]),
                    ("Longitud", fila["lon"]),
                    ("Bicis disponibles", fila["num_bikes_available"]),
                    ("Bicis dañadas", fila["num_bikes_disabled"]),
                    ("Puertos disponibles", fila["num_docks_available"]),
                    ("Puertos dañados", fila["num_docks_disabled"]),
                ]
            )
