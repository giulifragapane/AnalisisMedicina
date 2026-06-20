"""
╔════════════════════════════════════════════════════════════════╗
║   HITO 4 — Dashboard Interactivo de Desempeño Académico        ║
║   Grupo 51: García, Fragapane                                  ║
║                                                                ║
║   REQUISITO PREVIO: ejecutar importar_datos.py una sola vez    ║
║   EJECUCIÓN: streamlit run app_dashboard.py                    ║
╚════════════════════════════════════════════════════════════════╝
"""
 
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
 
# ══════════════════════════════════════════════════════════════════
# 0. VARIABLES DE ENTORNO  (.env nunca se sube a GitHub)
# ══════════════════════════════════════════════════════════════════
load_dotenv()
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST     = os.environ.get("DB_HOST")
DB_PORT     = os.environ.get("DB_PORT")
DB_NAME     = os.environ.get("DB_NAME")
 
PALETA_TRABAJA = {"No": "#4A90D9", "Sí": "#E8734A"}
PALETA_EDU     = {"Pública": "#4A90D9", "Privada": "#9B59B6"}
C_VERDE  = "#5BAD6F"
C_NARANJA= "#E8734A"
C_AZUL   = "#4A90D9"
C_ROJO   = "#D94A4A"
C_GRIS   = "#8E9AAF"
C_AMARILL= "#F0B429"
 
# ══════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Dashboard Académico · Medicina",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
sns.set_theme(style="whitegrid")
 
# ══════════════════════════════════════════════════════════════════
# 2. CONEXIÓN A MYSQL  (@st.cache_resource → engine una sola vez)
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def get_engine():
    """Crea y devuelve el motor SQLAlchemy. Se ejecuta una sola vez."""
    return create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        pool_pre_ping=True,
    )
 
try:
    engine = get_engine()
except Exception as e:
    st.error(f"❌ No se pudo conectar a MySQL: {e}")
    st.info("Verificá que XAMPP esté corriendo y que hayas ejecutado `importar_datos.py`.")
    st.stop()
 
# ══════════════════════════════════════════════════════════════════
# 3. FUNCIONES DE CONSULTA
#    pd.read_sql_query + params → sin SQL Injection
# ══════════════════════════════════════════════════════════════════
 
@st.cache_data(ttl=60)
def cargar_opciones_filtros() -> dict:
    """Valores únicos para widgets. ttl=60 → refresca cada minuto."""
    with engine.connect() as conn:
        def unicos(col):
            return pd.read_sql_query(
                f"SELECT DISTINCT `{col}` FROM estudiantes ORDER BY `{col}`", conn
            )[col].tolist()
        return {
            "años":    unicos("Año_Cursado"),
            "trabaja": unicos("Trabaja"),
            "tipo":    unicos("Tipo_Educacion"),
            "genero":  unicos("Género"),
        }
 
 
def consultar_estudiantes(años, trabaja, tipo, genero, nota_min, nota_max) -> pd.DataFrame:
    """
    MySQL filtra en el servidor → Python recibe solo lo necesario.
    Placeholders %s + params evitan SQL Injection (Clase 13).
    """
    def ph(lst): return ",".join(["%s"] * len(lst))
 
    query = f"""
        SELECT Id, Nombre, Género, Edad,
               Promedio_Notas, Asistencia_Clases_pct, TP_Entregados_pct,
               Trabaja, Tipo_Educacion, Año_Cursado,
               Materias_Aprobadas_Promedio, Demora_Traslado_min,
               Nivel_Asistencia, Regular, Indice_Compromiso, Categoria_Riesgo
        FROM estudiantes
        WHERE Año_Cursado    IN ({ph(años)})
          AND Trabaja        IN ({ph(trabaja)})
          AND Tipo_Educacion IN ({ph(tipo)})
          AND Género         IN ({ph(genero)})
          AND Promedio_Notas BETWEEN %s AND %s
    """
    params = tuple(años)+tuple(trabaja)+tuple(tipo)+tuple(genero)+(nota_min, nota_max)
    with engine.connect() as conn:
        return pd.read_sql_query(query, con=conn, params=params)
 
 
def consultar_p1_por_año() -> pd.DataFrame:
    """
    P1: GROUP BY ejecutado en MySQL.
    Regla de oro Clase 13: el servidor hace el trabajo pesado.
    Solo viajan los promedios, no los 5000 registros.
    """
    query = """
        SELECT Año_Cursado, Trabaja,
               ROUND(AVG(Promedio_Notas), 2) AS Promedio_Notas,
               COUNT(Id)                      AS Cantidad
        FROM estudiantes
        GROUP BY Año_Cursado, Trabaja
        ORDER BY Año_Cursado, Trabaja
    """
    with engine.connect() as conn:
        return pd.read_sql_query(query, con=conn)
 
 
# ══════════════════════════════════════════════════════════════════
# 4. SIDEBAR — FILTROS INTERACTIVOS
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("🎛️ Filtros")
    st.caption("Todos los gráficos y KPIs se actualizan en tiempo real.")
    st.divider()
 
    try:
        opc = cargar_opciones_filtros()
    except Exception as e:
        st.error(f"❌ Error al leer MySQL: {e}")
        st.stop()
 
    años_sel    = st.multiselect("📅 Año Cursado",       options=opc["años"],    default=opc["años"])
    trabaja_sel = st.multiselect("💼 ¿Trabaja?",         options=opc["trabaja"], default=opc["trabaja"])
    tipo_sel    = st.multiselect("🏫 Tipo de Educación", options=opc["tipo"],    default=opc["tipo"])
    genero_sel  = st.multiselect("👤 Género",            options=opc["genero"],  default=opc["genero"])
    st.divider()
    rango_notas = st.slider("📊 Rango de Promedio de Notas",
                             0.0, 10.0, (0.0, 10.0), step=0.5)
    st.divider()
    st.caption("Grupo 51 · TUP · Análisis de Datos 2026")
    st.caption(f"🟢 MySQL → `{DB_NAME}`")
 
if not all([años_sel, trabaja_sel, tipo_sel, genero_sel]):
    st.warning("⚠️ Seleccioná al menos una opción en cada filtro.")
    st.stop()
 
# ══════════════════════════════════════════════════════════════════
# 5. CONSULTA PRINCIPAL
# ══════════════════════════════════════════════════════════════════
try:
    df = consultar_estudiantes(años_sel, trabaja_sel, tipo_sel, genero_sel,
                                rango_notas[0], rango_notas[1])
except Exception as e:
    st.error(f"❌ Error en la consulta: {e}")
    st.stop()
 
if df.empty:
    st.warning("⚠️ Ningún registro coincide con los filtros. Ampliá los criterios.")
    st.stop()
 
# ══════════════════════════════════════════════════════════════════
# 6. ENCABEZADO
# ══════════════════════════════════════════════════════════════════
st.title("🎓 Dashboard de Desempeño Académico — Medicina")
st.markdown(
    f"**Grupo 51** · García, Fragapane · "
    f"Datos en tiempo real desde **MySQL** (`{DB_NAME}`)"
)
st.divider()
 
# Cálculos globales usados en múltiples secciones
bajo_rend_mask = (
    (df["Promedio_Notas"] < 6) &
    (df["TP_Entregados_pct"] < 60) &
    (df["Asistencia_Clases_pct"] < 70)
)
df_sí    = df[df["Trabaja"] == "Sí"]
df_no    = df[df["Trabaja"] == "No"]
df_bajo  = df[bajo_rend_mask]
df_resto = df[~bajo_rend_mask]
 
# ══════════════════════════════════════════════════════════════════
# UTILIDAD
# ══════════════════════════════════════════════════════════════════
def estilo(ax, titulo, xlabel="", ylabel=""):
    ax.set_title(titulo, fontsize=11, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.tick_params(labelsize=9)
    ax.spines[["top", "right"]].set_visible(False)
 
 
def gauge_matplotlib(ax, valor, maximo, titulo, color, fmt=".2f"):
    """Dibuja un gauge semicircular tipo Grafana."""
    theta = np.linspace(np.pi, 0, 200)
    # fondo gris
    ax.plot(np.cos(theta), np.sin(theta), color="#E0E0E0", linewidth=18, solid_capstyle="round")
    # valor coloreado
    pct   = min(valor / maximo, 1.0)
    theta2 = np.linspace(np.pi, np.pi - pct * np.pi, 200)
    ax.plot(np.cos(theta2), np.sin(theta2), color=color, linewidth=18, solid_capstyle="round")
    ax.text(0, -0.15, f"{valor:{fmt}}", ha="center", va="center",
            fontsize=20, fontweight="bold", color=color)
    ax.text(0, -0.55, titulo, ha="center", va="center",
            fontsize=9, color="#555", wrap=True)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.8, 1.2)
    ax.axis("off")
 
 
# ══════════════════════════════════════════════════════════════════
# 7. KPIs GLOBALES
# ══════════════════════════════════════════════════════════════════
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("👥 Estudiantes",       f"{len(df):,}")
k2.metric("📊 Promedio General",  f"{df['Promedio_Notas'].mean():.2f} / 10")
k3.metric("💼 Trabajan",          f"{(df['Trabaja']=='Sí').mean()*100:.1f}%")
k4.metric("✅ Regulares",         f"{(df['Regular']=='Sí').mean()*100:.1f}%")
k5.metric("⚠️ Alto Riesgo",       f"{(df['Categoria_Riesgo']=='Alto riesgo').mean()*100:.1f}%")
k6.metric("🔴 Bajo Rendimiento",  f"{bajo_rend_mask.mean()*100:.1f}%",
          help="Nota<6 + TPs<60% + Asistencia<70% simultáneamente")
st.divider()
 
 
# ══════════════════════════════════════════════════════════════════
# DASHBOARD 1 — PREGUNTA 1
# Réplica de Grafana: 2 stats + 2 barras por año + 1 stat diferencia
# ══════════════════════════════════════════════════════════════════
st.subheader("📌 Pregunta 1 — Impacto de trabajar en el promedio de notas")
st.markdown("*¿Cuál es la diferencia en el promedio de notas entre estudiantes que "
            "trabajan y los que no, y esa diferencia se mantiene en todos los años?*")
 
prom_no = df_no["Promedio_Notas"].mean() if len(df_no) > 0 else 0
prom_sí = df_sí["Promedio_Notas"].mean() if len(df_sí) > 0 else 0
dif_p1  = prom_no - prom_sí
 
# Fila 1: stats + diferencia (igual a Grafana)
r1a, r1b, r1c = st.columns(3)
r1a.metric("📊 Promedio de Notas — No trabajan", f"{prom_no:.2f}")
r1b.metric("📊 Promedio de Notas — Trabajan",    f"{prom_sí:.2f}")
r1c.metric("↕️ Diferencia (No trabaja − Trabaja)",
           f"{dif_p1:+.2f}",
           delta_color="normal" if dif_p1 >= 0 else "inverse")
 
# Fila 2: barras por año (igual a Grafana)
try:
    datos_año = consultar_p1_por_año()
    datos_año = datos_año[
        datos_año["Año_Cursado"].isin(años_sel) &
        datos_año["Trabaja"].isin(trabaja_sel)
    ]
except Exception:
    datos_año = df.groupby(["Año_Cursado","Trabaja"])["Promedio_Notas"].mean().reset_index()
    datos_año.columns = ["Año_Cursado","Trabaja","Promedio_Notas"]
 
col_b1, col_b2 = st.columns(2)
 
with col_b1:
    d_si = datos_año[datos_año["Trabaja"]=="Sí"].sort_values("Año_Cursado")
    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.bar([f"{int(a)}°" for a in d_si["Año_Cursado"]],
                  d_si["Promedio_Notas"], color=PALETA_TRABAJA["Sí"],
                  alpha=0.88, edgecolor="white")
    ax.bar_label(bars, fmt="%.2f", fontsize=9, padding=3, fontweight="bold")
    ax.set_ylim(0, 10)
    ax.axhline(6, color=C_ROJO, linestyle="--", linewidth=1, alpha=0.6, label="Mínimo (6)")
    estilo(ax, "Promedio de Notas — Alumnos que TRABAJAN por Año",
           "Año de Carrera", "Promedio de Notas")
    ax.legend(fontsize=8)
    fig.tight_layout()
    st.pyplot(fig) 
    plt.close(fig)
 
with col_b2:
    d_no = datos_año[datos_año["Trabaja"]=="No"].sort_values("Año_Cursado")
    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.bar([f"{int(a)}°" for a in d_no["Año_Cursado"]],
                  d_no["Promedio_Notas"], color=PALETA_TRABAJA["No"],
                  alpha=0.88, edgecolor="white")
    ax.bar_label(bars, fmt="%.2f", fontsize=9, padding=3, fontweight="bold")
    ax.set_ylim(0, 10)
    ax.axhline(6, color=C_ROJO, linestyle="--", linewidth=1, alpha=0.6, label="Mínimo (6)")
    estilo(ax, "Promedio de Notas — Alumnos que NO TRABAJAN por Año",
           "Año de Carrera", "Promedio de Notas")
    ax.legend(fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
 
st.info(
    "📌 **Conclusión:** Los alumnos que **no trabajan** tienen un promedio levemente superior "
    f"({prom_no:.2f} vs {prom_sí:.2f}, diferencia de {abs(dif_p1):.2f} pts). "
    "Las barras por año muestran que la brecha **no es sostenida ni creciente**: "
    "en 1° año es la mayor (0.30 pts), pero en 2° y 6° la relación se invierte. "
    "El impacto de trabajar es **estable y no acumulativo** a lo largo de la carrera."
)
st.divider()
 
 
# ══════════════════════════════════════════════════════════════════
# DASHBOARD 2 — PREGUNTA 2
# Réplica de Grafana: 2 pies + 2 gauges + 2 stats + 2 barras por tipo
# ══════════════════════════════════════════════════════════════════
st.subheader("📌 Pregunta 2 — Asistencia y materias aprobadas por tipo de educación")
st.markdown("*¿Los estudiantes con asistencia mayor al 75% aprueban más materias, "
            "y cómo varía eso según el tipo de educación (pública o privada)?*")
 
df_alta = df[df["Nivel_Asistencia"] == "Alta"]
df_baja = df[df["Nivel_Asistencia"] == "Baja"]
n_total = len(df)
 
pct_alta_pub = len(df_alta[df_alta["Tipo_Educacion"]=="Pública"]) / max(len(df[df["Tipo_Educacion"]=="Pública"]), 1) * 100
pct_alta_priv= len(df_alta[df_alta["Tipo_Educacion"]=="Privada"]) / max(len(df[df["Tipo_Educacion"]=="Privada"]), 1) * 100
pct_baja_pub = 100 - pct_alta_pub
pct_baja_priv= 100 - pct_alta_priv
pct_alta_total = len(df_alta) / n_total * 100
pct_baja_total = len(df_baja) / n_total * 100
mat_alta = df_alta["Materias_Aprobadas_Promedio"].mean()
mat_baja = df_baja["Materias_Aprobadas_Promedio"].mean()
 
# Fila 1: stats de materias aprobadas + gauges de porcentaje (igual a Grafana)
s1, s2, g1, g2 = st.columns(4)
s1.metric("📚 Materias aprobadas — Asistencia Alta (>75%)", f"{mat_alta:.2f}")
s2.metric("📚 Materias aprobadas — Asistencia Baja (≤75%)", f"{mat_baja:.2f}")
 
with g1:
    fig, ax = plt.subplots(figsize=(3, 2.2))
    gauge_matplotlib(ax, pct_alta_total, 100,
                     "% estudiantes\nasistencia alta", C_VERDE, fmt=".1f")
    st.pyplot(fig)
    plt.close(fig)
 
with g2:
    fig, ax = plt.subplots(figsize=(3, 2.2))
    gauge_matplotlib(ax, pct_baja_total, 100,
                     "% estudiantes\nasistencia baja", C_NARANJA, fmt=".1f")
    st.pyplot(fig)
    plt.close(fig)
 
# Fila 2: pies por tipo de educación (igual a Grafana)
col_pie1, col_pie2 = st.columns(2)
 
with col_pie1:
    fig, axes = plt.subplots(1, 2, figsize=(7, 3.5))
    for ax, tipo, pct_alta, pct_baja in zip(
        axes,
        ["Pública", "Privada"],
        [pct_alta_pub, pct_alta_priv],
        [pct_baja_pub, pct_baja_priv],
    ):
        ax.pie(
            [pct_alta, pct_baja],
            labels=[f"Alta\n{pct_alta:.1f}%", f"Baja\n{pct_baja:.1f}%"],
            colors=[C_VERDE, C_NARANJA],
            startangle=90,
            textprops={"fontsize": 9},
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        )
        ax.set_title(f"Asistencia — {tipo}", fontsize=10, fontweight="bold")
    fig.suptitle("Porcentaje de estudiantes por nivel de asistencia\nsegún tipo de educación",
                 fontsize=11, fontweight="bold")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
 
# Fila 3: barras de materias por tipo (igual a Grafana)
with col_pie2:
    resumen = (
        df.groupby(["Tipo_Educacion","Nivel_Asistencia"])["Materias_Aprobadas_Promedio"]
        .mean().reset_index()
    )
    tipos = ["Pública", "Privada"]
    x = np.arange(len(tipos))
    ancho = 0.35
 
    fig, axes = plt.subplots(1, 2, figsize=(7, 3.5))
    for ax, nivel, color, titulo in zip(
        axes,
        ["Alta", "Baja"],
        [C_VERDE, C_NARANJA],
        ["Materias aprobadas por tipo de educ.\n— Asistencia Alta",
         "Materias aprobadas por tipo de educ.\n— Asistencia Baja"],
    ):
        vals = [
            resumen[(resumen["Tipo_Educacion"]==t) & (resumen["Nivel_Asistencia"]==nivel)]
            ["Materias_Aprobadas_Promedio"].values
            for t in tipos
        ]
        vals = [v[0] if len(v)>0 else 0 for v in vals]
        bars = ax.bar(tipos, vals, color=color, alpha=0.88, edgecolor="white")
        ax.bar_label(bars, fmt="%.2f", fontsize=10, padding=3, fontweight="bold")
        ax.set_ylim(0, 5)
        estilo(ax, titulo, "Tipo de Educación", "Materias Aprobadas")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
 
st.info(
    "📌 **Conclusión:** Las diferencias son mínimas en ambos sentidos. "
    f"Asistencia alta: **{mat_alta:.2f} materias** | Baja: **{mat_baja:.2f} materias**. "
    "En pública: baja asistencia → 3.00 vs alta → 2.94. "
    "En privada: alta → 3.01 vs baja → 2.99. "
    "**Ni la asistencia ni el tipo de educación son factores determinantes** "
    "en la cantidad de materias aprobadas."
)
st.divider()
 
 
# ══════════════════════════════════════════════════════════════════
# DASHBOARD 3 — PREGUNTA 3
# Réplica de Grafana: 1 stat + 1 gauge + 2 stats demora + 2 barras
# ══════════════════════════════════════════════════════════════════
st.subheader("📌 Pregunta 3 — Perfil del estudiante con bajo rendimiento")
st.markdown("*¿Qué porcentaje de estudiantes tiene simultáneamente nota<6, "
            "TPs<60% y asistencia<70%, y cuál es su demora de traslado?*")
 
n_bajo    = len(df_bajo)
pct_bajo  = bajo_rend_mask.mean() * 100
dem_bajo  = df_bajo["Demora_Traslado_min"].mean()  if n_bajo > 0 else 0
dem_resto = df_resto["Demora_Traslado_min"].mean() if len(df_resto) > 0 else 0
 
# Fila 1: stat + gauge + 2 stats demora (igual a Grafana)
s1, g1, s2, s3 = st.columns(4)
s1.metric("🔴 Estudiantes con bajo rendimiento", f"{n_bajo}",
          help="Nota<6 + TPs<60% + Asistencia<70% simultáneamente")
 
with g1:
    fig, ax = plt.subplots(figsize=(3, 2.2))
    gauge_matplotlib(ax, pct_bajo, 100,
                     "% del total\nen riesgo", C_ROJO, fmt=".1f")
    st.pyplot(fig)
    plt.close(fig)
 
s2.metric("🚌 Demora traslado — Grupo en riesgo", f"{dem_bajo:.1f} min")
s3.metric("🚌 Demora traslado — Resto",           f"{dem_resto:.1f} min")
 
# Fila 2: barras por año y por tipo de educación (igual a Grafana)
col_b1, col_b2 = st.columns(2)
 
with col_b1:
    if n_bajo > 0:
        dist_año = df_bajo["Año_Cursado"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        bars = ax.bar([f"{int(a)}° año" for a in dist_año.index],
                      dist_año.values,
                      color=C_ROJO, alpha=0.85, edgecolor="white")
        ax.bar_label(bars, fmt="%d", fontsize=10, padding=3, fontweight="bold")
        estilo(ax, "Cantidad de estudiantes con bajo rendimiento\npor año de cursado",
               "Año de Carrera", "Cantidad")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Sin estudiantes en perfil crítico para los filtros activos.")
 
with col_b2:
    if n_bajo > 0:
        dist_tipo = df_bajo["Tipo_Educacion"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        colores_tipo = [PALETA_EDU.get(t, C_GRIS) for t in dist_tipo.index]
        bars = ax.bar(dist_tipo.index, dist_tipo.values,
                      color=colores_tipo, alpha=0.85, edgecolor="white")
        ax.bar_label(bars, fmt="%d", fontsize=10, padding=3, fontweight="bold")
        estilo(ax, "Distribución de estudiantes en riesgo\npor tipo de educación",
               "Tipo de Educación", "Cantidad")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Sin datos para los filtros activos.")
 
dif = abs(dem_bajo - dem_resto)
st.info(
    f"📌 **Conclusión:** El **{pct_bajo:.1f}% de los estudiantes ({n_bajo} casos)** cumple "
    "las tres condiciones simultáneamente, representando el núcleo más vulnerable. "
    f"La demora de traslado del grupo crítico (**{dem_bajo:.1f} min**) es apenas "
    f"**{dif:.1f} minutos** más que el resto (**{dem_resto:.1f} min**). "
    "Esta diferencia no es significativa: el traslado **no es un factor determinante** "
    "del bajo rendimiento. Puede actuar como un factor contextual que, en combinación "
    "con la baja asistencia y la escasa entrega de TPs, dificulta la regularidad académica."
)
st.divider()
 
 
# ══════════════════════════════════════════════════════════════════
# 8. TABLA Y ESTADÍSTICAS EXPANDIBLES
# ══════════════════════════════════════════════════════════════════
with st.expander("🔎 Ver registros devueltos según los filtros activos"):
    cols_tabla = [
        "Nombre","Género","Edad","Año_Cursado","Tipo_Educacion","Trabaja",
        "Promedio_Notas","Asistencia_Clases_pct","TP_Entregados_pct",
        "Materias_Aprobadas_Promedio","Indice_Compromiso","Regular","Categoria_Riesgo",
    ]
    st.dataframe(
        df[[c for c in cols_tabla if c in df.columns]].reset_index(drop=True),
        width="stretch", height=300,
    )
    st.caption(f"MySQL devolvió {len(df):,} registros para los filtros activos.")
 
with st.expander("📋 Estadísticas descriptivas del subconjunto filtrado"):
    cols_num = [
        "Promedio_Notas","Asistencia_Clases_pct","TP_Entregados_pct",
        "Materias_Aprobadas_Promedio","Demora_Traslado_min","Indice_Compromiso",
    ]
    st.dataframe(
        df[[c for c in cols_num if c in df.columns]].describe().round(2),
        width="stretch",
    )
 
# ══════════════════════════════════════════════════════════════════
# 9. PIE DE PÁGINA
# ══════════════════════════════════════════════════════════════════
st.divider()
st.markdown(
    "<div style='text-align:center; color:#8E9AAF; font-size:12px;'>"
    "Trabajo Práctico Integrador — Hito 4 · "
    "Grupo 51: García, Fragapane · "
    "Tecnicatura Universitaria en Programación · 2026"
    "</div>",
    unsafe_allow_html=True,
)