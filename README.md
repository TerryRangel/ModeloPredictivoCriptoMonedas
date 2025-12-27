#  Sistema Cuantitativo de Trading de Bitcoin (Trend + ML + Volatility Target)

Este proyecto implementa una estrategia de trading algorítmico de grado institucional para Bitcoin. A diferencia de los bots convencionales que buscan "hacerse rico rápido", este sistema está diseñado con una mentalidad **defensiva**. Su prioridad absoluta es la **gestión de riesgo** y la **protección del capital** ante los colapsos del mercado.

> **Filosofía:** "Primero sobrevivir, luego ganar. En un activo tan volátil como Bitcoin, evitar las pérdidas catastróficas del -80% es matemáticamente más valioso que intentar capturar cada subida. Protegemos el capital a toda costa para permitir que el interés compuesto funcione."

---

##  Características del Algoritmo (v3.0)

El modelo ha evolucionado a una versión robusta, eliminando el sesgo de anticipación (*look-ahead bias*) e integrando múltiples capas de seguridad:

### 1. El "Escudo" de Tendencia (SMA 50)
* **Regla:** Solo operamos si el precio está **por encima de su Media Móvil de 50 días**.
* **Función:** Actúa como un cortafuegos. Si el mercado entra en una tendencia bajista (como en 2018 o 2022), el sistema se apaga automáticamente y se queda en Dólares.

### 2. Machine Learning "Honesto" (Walk-Forward)
* **Modelo:** Random Forest Classifier.
* **Función:** No intenta adivinar el precio. Su único trabajo es predecir **peligro**. Si la IA detecta alta probabilidad de un crash inminente, veta las señales de compra.

### 3. Volatility Targeting (Gestión de Posición)
* El sistema nunca apuesta "todo o nada". Ajusta el tamaño de la inversión diariamente:
    * **Mercado Seguro:** Aumenta la exposición (hasta 100%).
    * **Mercado Incierto:** Reduce la exposición (al 30%, 10% o 0%).

---

## 📊 Resultados Anuales (Backtest 2015-2025)

*Validación realizada sin Data Leakage (Walk-Forward).*

| AÑO | ESTRATEGIA | MERCADO (BTC) | DIFERENCIA | DD ESTRATEGIA | DD MERCADO |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2015** | 0.00% | 22.63% | -22.63% | 0.00% | -42.63% |
| **2016** | 0.00% | 98.80% | -98.80% | 0.00% | -31.03% |
| **2017** | 92.28% | 838.03% | -745.75% | -15.74% | -37.94% |
| **2018** | **-9.14%** | **-81.29%** | **+72.15%** | **-15.47%** | **-86.54%** |
| **2019** | 81.44% | 53.20% | +28.23% | -18.10% | -55.12% |
| **2020** | 167.95% | 185.60% | -17.65% | -21.41% | -59.66% |
| **2021** | 37.71% | 15.55% | +22.17% | -13.54% | -58.22% |
| **2022** | **-22.37%** | **-71.09%** | **+48.72%** | **-23.39%** | **-73.07%** |
| **2023** | 77.93% | 132.67% | -54.74% | -12.51% | -20.80% |
| **2024** | 43.91% | 92.02% | -48.12% | -25.09% | -31.53% |
| **2025** | 5.02% | -14.27% | +19.28% | -9.96% | -33.12% |

###  Resumen Final
| Métrica | Estrategia (Trend + ML) | Mercado (Buy & Hold) |
| :--- | :--- | :--- |
| **Retorno Total** | **2,341.61%** | 2,295.37% |
| **Riesgo Máximo (Drawdown)** | **-30.03%** | **-88.64%** |
| **Días en Mercado** | 1,374 días | 4,008 días |

> **Conclusión:** La estrategia logró superar al mercado a largo plazo, pero lo más importante es que **redujo el riesgo casi 3 veces**. Mientras el inversor promedio perdía el 88% de su dinero en los peores momentos, la estrategia solo bajó un 30%.

---

##  Ejemplo de Uso e Interpretación

Para utilizar el sistema en tu día a día, utiliza el script `custom_simulator_split.py`. Este funciona como un **Asistente de Inversión** que te dice exactamente qué hacer con tu dinero.

### 1. Ejecutar el Simulador
```bash
python simulator.py



Cómo leer la salida (Ejemplo Real)
Imagina que tienes un capital total de $10,000 USD. El simulador te mostrará algo así:

Plaintext

FECHA      | PRECIO   | RIESGO | TOTAL (USD) | EN BITCOIN ($) | EN DÓLARES ($) | ORDEN DE TRADING
2025-06-15 | $98,000  | 60%    | $10,000     | $6,000         | $4,000         | 🟢 COMPRA: $1,000 (0.01 BTC)
Explicación paso a paso:

RIESGO (60%): El modelo ha calculado que hoy es seguro tener el 60% de tu dinero invertido.

EN BITCOIN ($6,000): Te dice que tu posición ideal en Bitcoin debería valer $6,000 dólares hoy.

EN DÓLARES ($4,000): Te dice que debes guardar $4,000 dólares en efectivo (USDT) como reserva de seguridad.

ORDEN DE TRADING: Como ayer tenías menos (digamos $5,000 en BTC), hoy el sistema te ordena: "Saca $1,000 de tu reserva y COMPRA Bitcoin" para llegar al nivel óptimo.



## 📂 Estructura del Proyecto

El flujo de trabajo es secuencial y modular:

```text

MODELOPREDICTIVOCRIPTOMONEDAS/
│
├── AnalisisdelModelo/              # Reportes, gráficas y diagnósticos
│   ├── garch_diagnostics.py        # Validación del modelo de volatilidad
│   ├── volatility_diagnostics.py   # Análisis de residuos
│   └── reporte_anual.csv           # Archivo de métricas generadas
│
│
├── 1. DATOS Y PREPARACIÓN
│   ├── data_loader.py              # Descarga precios históricos actualizados
│   ├── regime_dataset_builder.py   # Calcula volatilidad GARCH y define regímenes
│   └── bitcoin_prices.csv          # Base de datos de precios
│
├── 2. INTELIGENCIA ARTIFICIAL
│   ├── ml_regime_model.py          # Entrena el modelo (Walk-Forward)
│   ├── bitcoin_regime_dataset.csv  # Dataset de entrenamiento
│   └── bitcoin_regime_dataset_future_ml.csv # Predicciones generadas
│
├── 3. LÓGICA DE TRADING
│   ├── trading_rules.py            # EL CEREBRO: SMA50 + Vol Target + IA rules
│   └── bitcoin_trading_signals.csv # Señales finales (Buy/Sell) y tamaño de posición
│
├── 4. EJECUCIÓN Y SIMULACIÓN
│   ├── backtesting_engine.py       # Backtest rápido matemático
│   ├── simulator.py   # SIMULADOR VISUAL (Bitcoin vs Dólares)
│   ├── daily_trading_decision.py   # Consultar decisión de HOY
│   └── run.py                      # Pipeline automático
│
└── README.md                       # Documentación


Clonar el repositorio:

Bash

git clone <URL_DE_LA_REPO>
cd ModeloPredictivoCriptoMonedas
Instalar librerías:

Bash

pip install -r requirements.txt
Ejecutar el modelo:

Bash

python run.py
⚠️ Disclaimer
Este software es una herramienta de investigación cuantitativa. El trading de criptomonedas conlleva un alto riesgo de pérdida.

El rendimiento pasado (2341%) no garantiza resultados futuros.

El modelo está diseñado para proteger, pero ninguna estrategia es infalible.

Úsalo bajo tu propia responsabilidad y nunca inviertas dinero que no puedas permitirte perder.

