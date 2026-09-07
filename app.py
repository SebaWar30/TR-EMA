import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Screener de Trading 9 Criterios", page_icon="📈", layout="centered")

st.title("📈 Screener de Trading Semanal")
st.markdown("Analiza la estructura de medias móviles (EMA 5, 20, 70, 200) en temporalidad semanal.")

# Formulario de entrada
with st.form("search_form"):
    ticker_input = st.text_input("Ingresa el TICKER (ej: AAPL, NVDA, TSLA, BTC-USD):", value="NVDA").upper().strip()
    submitted = st.form_submit_button("🔍 Analizar Activo")

if submitted and ticker_input:
    with st.spinner("Descargando datos y evaluando criterios..."):
        try:
            ticker = yf.Ticker(ticker_input)
            df = ticker.history(period="5y", interval="1wk")
            
            if df.empty or len(df) < 200:
                st.error(f"❌ No hay suficientes datos para {ticker_input} (se requieren mínimo 200 semanas de historial).")
            else:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                    
                cierre = df['Close']
                
                # EMAs
                ema5 = cierre.ewm(span=5, adjust=False).mean()
                ema20 = cierre.ewm(span=20, adjust=False).mean()
                ema70 = cierre.ewm(span=70, adjust=False).mean()
                ema200 = cierre.ewm(span=200, adjust=False).mean()
                
                p_act = cierre.iloc[-1]
                
                e5_act, e5_prev = ema5.iloc[-1], ema5.iloc[-2]
                e20_act, e20_prev = ema20.iloc[-1], ema20.iloc[-2]
                e70_act, e70_prev = ema70.iloc[-1], ema70.iloc[-2]
                e200_act, e200_prev = ema200.iloc[-1], ema200.iloc[-2]
                
                # Evaluaciones
                criterios = {
                    "1. EMA 5 al alza": e5_act > e5_prev,
                    "2. EMA 20 al alza": e20_act > e20_prev,
                    "3. EMA 70 al alza": e70_act > e70_prev,
                    "4. EMA 200 al alza": e200_act > e200_prev,
                    "5. EMA 5 sobre EMA 20 (Cruce)": e5_act > e20_act,
                    "6. Precio sobre EMA 5": p_act > e5_act,
                    "7. Precio sobre EMA 20": p_act > e20_act,
                    "8. Precio sobre EMA 70": p_act > e70_act,
                    "9. Precio sobre EMA 200": p_act > e200_act,
                }
                
                puntuacion = sum(criterios.values())
                
                # Despliegue de Resultados
                st.markdown("---")
                col1, col2 = st.columns(2)
                col1.metric("Precio Cierre Semanal", f"${p_act:.2f}")
                col2.metric("Puntuación Final", f"{puntuacion} / 9")
                
                st.subheader("Estado de las Medias Móviles")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("EMA 5", f"${e5_act:.2f}", "Al alza" if e5_act > e5_prev else "A la baja")
                m2.metric("EMA 20", f"${e20_act:.2f}", "Al alza" if e20_act > e20_prev else "A la baja")
                m3.metric("EMA 70", f"${e70_act:.2f}", "Al alza" if e70_act > e70_prev else "A la baja")
                m4.metric("EMA 200", f"${e200_act:.2f}", "Al alza" if e200_act > e200_prev else "A la baja")
                
                st.subheader("Desglose de Criterios")
                for crit, cumplido in criterios.items():
                    if cumplido:
                        st.success(f"✅ {crit}")
                    else:
                        st.error(f"❌ {crit}")
                        
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
