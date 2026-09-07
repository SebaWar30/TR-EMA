import yfinance as yf
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output

def analizar_criterios_semanales(ticker_symbol):
    ticker_symbol = ticker_symbol.upper().strip()
    if not ticker_symbol:
        print("⚠️ Por favor ingresa un Ticker válido.")
        return

    print(f"🔄 Obteniendo datos para {ticker_symbol}...")
    
    try:
        # Descargamos 5 años de datos semanales para asegurar el cálculo correcto de la EMA 200
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="5y", interval="1wk")
        
        if df.empty or len(df) < 200:
            print(f"❌ No hay suficientes datos para {ticker_symbol} (Se requieren al menos 200 semanas de historial).")
            return

        # Aplanar la estructura del DataFrame
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        cierre = df['Close']
        
        # 1. Cálculo de Medias Móviles Exponenciales (EMAs)
        ema5 = cierre.ewm(span=5, adjust=False).mean()
        ema20 = cierre.ewm(span=20, adjust=False).mean()
        ema70 = cierre.ewm(span=70, adjust=False).mean()
        ema200 = cierre.ewm(span=200, adjust=False).mean()
        
        # Precios y EMAs actuales vs. semana anterior
        p_act = cierre.iloc[-1]
        
        e5_act, e5_prev = ema5.iloc[-1], ema5.iloc[-2]
        e20_act, e20_prev = ema20.iloc[-1], ema20.iloc[-2]
        e70_act, e70_prev = ema70.iloc[-1], ema70.iloc[-2]
        e200_act, e200_prev = ema200.iloc[-1], ema200.iloc[-2]
        
        # 2. Evaluación de los 9 Puntos Técnicos
        criterios = {
            "1. EMA 5 al alza": e5_act > e5_prev,
            "2. EMA 20 al alza": e20_act > e20_prev,
            "3. EMA 70 al alza": e70_act > e70_prev,
            "4. EMA 200 al alza": e200_act > e200_prev,
            "5. EMA 5 cruza/sobre EMA 20": e5_act > e20_act,
            "6. Precio sobre EMA 5": p_act > e5_act,
            "7. Precio sobre EMA 20": p_act > e20_act,
            "8. Precio sobre EMA 70": p_act > e70_act,
            "9. Precio sobre EMA 200": p_act > e200_act,
        }
        
        puntuacion = sum(criterios.values())
        
        # 3. Mostrar Resultados en Pantalla
        clear_output(wait=True)
        display(ui) # Mantiene el buscador arriba
        
        print("\n" + "="*50)
        print(f"📊 SISTEMA DE TRADING - ANÁLISIS PARA: {ticker_symbol}")
        print("="*50)
        print(f"💵 Precio Cierre Semanal: ${p_act:.2f}")
        print(f"📈 PUNTUACIÓN TOTAL: {puntuacion} DE 9 CRITERIOS CUMPLIDOS")
        print("="*50)
        
        print("\n--- VALORES DE LAS MEDIAS MÓVILES ---")
        print(f"• EMA 5:   ${e5_act:.2f}  ({'▲ Al alza' if e5_act > e5_prev else '▼ A la baja'})")
        print(f"• EMA 20:  ${e20_act:.2f}  ({'▲ Al alza' if e20_act > e20_prev else '▼ A la baja'})")
        print(f"• EMA 70:  ${e70_act:.2f}  ({'▲ Al alza' if e70_act > e70_prev else '▼ A la baja'})")
        print(f"• EMA 200: ${e200_act:.2f}  ({'▲ Al alza' if e20_act > e20_prev else '▼ A la baja'})")
        
        print("\n--- DESGLOSE DE LOS 9 CRITERIOS ---")
        for crit, cumplido in criterios.items():
            simbolo = "✅ SI" if cumplido else "❌ NO"
            print(f"{simbolo:<6} | {crit}")
            
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ Ocurrió un error al consultar el ticker: {e}")

# --- CREACIÓN DE LA INTERFAZ GRÁFICA ---
text_ticker = widgets.Text(
    value='NVDA',
    placeholder='Escribe el ticker (ej: AAPL, NVDA, TSLA)',
    description='Ticker:',
    disabled=False
)

button_search = widgets.Button(
    description='🔍 Analizar Ticker',
    button_style='success',
    tooltip='Buscar y analizar'
)

output = widgets.Output()

def on_button_clicked(b):
    with output:
        analizar_criterios_semanales(text_ticker.value)

button_search.on_click(on_button_clicked)

# Desplegar interfaz
ui = widgets.HBox([text_ticker, button_search])
display(ui, output)
