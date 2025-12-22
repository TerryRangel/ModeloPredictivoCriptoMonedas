Modelo Predictivo de Bitcoin con Regímenes, GARCH y Machine Learning

Este proyecto implementa un modelo cuantitativo de trading aplicado a Bitcoin, cuyo objetivo principal es reducir el riesgo (drawdown) y tomar decisiones más racionales de compra, venta o mantenerse fuera del mercado.

El modelo no intenta predecir el precio exacto, sino identificar regímenes de mercado y actuar solo cuando las condiciones son favorables.

Objetivo del proyecto

Identificar regímenes de mercado (favorable, neutro, adverso)

Usar volatilidad (GARCH) como medida de riesgo

Incorporar Machine Learning para anticipar regímenes futuros

Generar señales de trading disciplinadas

Reducir drawdown frente a una estrategia pasiva (buy & hold)

Resultados principales (2020–2025)
Retorno total estrategia: 66.87%
Retorno total mercado:    241.19%

Drawdown máximo estrategia: -34.81%
Drawdown máximo mercado:    -83.72%

Días invertido: 934 de 2171


La estrategia sacrifica retorno total a cambio de una reducción significativa del riesgo, lo cual es el objetivo principal.

Requisitos

Antes de ejecutar el proyecto necesitas:

Python 3.9 o superior

Git

Conexión a internet (para descargar datos si se desea actualizar)

Librerías utilizadas

pandas

numpy

matplotlib

statsmodels

arch

scikit-learn

yfinance (opcional, para descarga de datos)

Instalación

Clona el repositorio:

git clone <URL_DEL_REPOSITORIO>
cd ModeloPredictivoCriptoMonedas


Crea y activa el entorno virtual:

python -m venv venv
venv\Scripts\activate   # Windows


Instala dependencias:

pip install -r requirements.txt


(Si no tienes requirements.txt, instala manualmente las librerías listadas arriba).

Cosas importantes antes de ejecutar

Los scripts dependen de archivos CSV generados por pasos anteriores.

No ejecutes todo al azar: el proyecto sigue un flujo lógico.

Las fechas y periodos pueden cambiar los resultados.

El modelo no incluye costos de transacción.

Estructura del proyecto y explicación de archivos
MODELOPREDICTIVOCRIPTOMONEDAS/
│
├── AnalisisdelModelo/
│   └── Reportes, gráficas y análisis manuales
│
├── venv/
│   └── Entorno virtual
│
├── bitcoin_prices.csv
│   └── Precios históricos de Bitcoin (datos base)
│
├── data_loader.py
│   └── Descarga o carga de datos históricos
│
├── garch_model.py
│   └── Modelo GARCH para estimar volatilidad
│
├── garch_diagnostics.py
│   └── Validación del modelo GARCH (ARCH-LM, residuos)
│
├── regime_dataset_builder.py
│   └── Construye el dataset de características (features)
│
├── bitcoin_regime_dataset.csv
│   └── Dataset con retornos, volatilidad y régimen actual
│
├── ml_regime_model.py
│   └── Modelo de Machine Learning que predice régimen futuro
│
├── bitcoin_regime_dataset_ml.csv
│   └── Dataset preparado para entrenamiento ML
│
├── bitcoin_regime_dataset_future_ml.csv
│   └── Dataset con predicción de régimen a t+5
│
├── trading_rules.py
│   └── Reglas de trading (compra / salida / exposición)
│
├── bitcoin_trading_signals.csv
│   └── Señales finales generadas por el modelo
│
├── backtesting_engine.py
│   └── Simulación histórica de la estrategia
│
├── daily_trading_decision.py
│   └── Script para obtener la decisión del día actual
│
└── README.md

Flujo recomendado de ejecución

Ejecuta los scripts en este orden:

Cargar o actualizar datos:

python data_loader.py


Calcular volatilidad:

python garch_model.py
python garch_diagnostics.py


Construir dataset de regímenes:

python regime_dataset_builder.py


Entrenar modelo ML:

python ml_regime_model.py


Generar señales de trading:

python trading_rules.py


Evaluar resultados:

python backtesting_engine.py

Tipo de modelo

Modelo cuantitativo basado en reglas

Machine Learning como filtro de riesgo, no como oráculo

Perfil conservador–balanceado

Enfocado en supervivencia del capital

Limitaciones

No considera comisiones ni slippage

Resultados dependen del periodo analizado

No garantiza resultados futuros

Bitcoin es un activo altamente volátil

Trabajo futuro

Ajuste automático de exposición

Métricas Sharpe / Sortino

Walk-forward analysis

Datos intradía

Aplicación a otros activos