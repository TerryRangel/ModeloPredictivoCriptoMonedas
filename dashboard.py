import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Centinela Dashboard", layout="wide")
st.title("🛡️ Centinela: Panel de Control")

# 1. Cargar los datos EXACTOS de tu CSV
@st.cache_data
def load_data():
    # Carga el archivo que generó tu script
    df = pd.read_csv("bitcoin_daily_decisions.csv", parse_dates=["Date"], index_col="Date")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Archivo 'bitcoin_daily_decisions.csv' no encontrado. Ejecuta tu modelo primero.")
    st.stop()

# Obtener los datos del último día (Hoy)
ultima_fila = df.iloc[-1]
fecha_hoy = df.index[-1].strftime('%Y-%m-%d')

st.markdown(f"### Estado Actual: **{fecha_hoy}**")

# 2. Mostrar las Métricas Principales (Tarjetas KPI)
col1, col2, col3, col4 = st.columns(4)

with col1:
    decision_color = "🟢" if ultima_fila["decision"] == "COMPRAR" else "🔴" if ultima_fila["decision"] == "SALIR" else "⚪"
    st.metric(label="Decisión de Hoy", value=f"{ultima_fila['decision']} {decision_color}")

with col2:
    estado_ia = "Seguro (0/1)" if ultima_fila["regime"] <= 1 else "Peligro (2)"
    st.metric(label="Régimen IA", value=estado_ia)

with col3:
    st.metric(label="Volatilidad Actual", value=f"{ultima_fila['volatility']:.4f}")

with col4:
    st.metric(label="Tendencia Vol (5d)", value=f"{ultima_fila['vol_trend_5']:.4f}")

st.divider()

# 3. Mostrar el Historial Visual
st.markdown("### Historial de Volatilidad y Decisiones")

# Crear un gráfico interactivo con Plotly usando tus datos
fig = px.line(df, y="volatility", title="Evolución de la Volatilidad GARCH", 
              labels={"volatility": "Volatilidad", "Date": "Fecha"})

# Agregar una línea para mostrar los días de "SALIR" como puntos rojos de alerta
df_salidas = df[df["decision"] == "SALIR"]
fig.add_scatter(x=df_salidas.index, y=df_salidas["volatility"], mode='markers', 
                marker=dict(color='red', size=8), name="Señal SALIR")

# Agregar puntos verdes para COMPRAR
df_compras = df[df["decision"] == "COMPRAR"]
fig.add_scatter(x=df_compras.index, y=df_compras["volatility"], mode='markers', 
                marker=dict(color='green', size=8), name="Señal COMPRAR")

st.plotly_chart(fig, use_container_width=True)

# 4. Mostrar la Tabla Cruda de los últimos 10 días (Igual que tu print)
st.markdown("### Últimas 10 Decisiones")
st.dataframe(df.tail(10))