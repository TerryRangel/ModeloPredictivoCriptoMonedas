import subprocess
import sys
import time

scripts = [
    "data_loader.py",              # 1. Descarga datos actualizados
    "regime_dataset_builder.py",   # 2. Calcula indicadores y regímenes 
    "ml_regime_model.py",          # 3. Entrena el modelo con los nuevos datos
    "trading_rules.py",            # 4. Genera las señales de compra/venta
    "backtesting_engine.py",
    "daily_trading_decision.py"                # 5. Muestra los resultados finales
    ""
]


print(" INICIANDO ........")


start_total = time.time()

for script in scripts:
    print(f">>> Ejecutando: {script}...")
    start_script = time.time()
    
    result = subprocess.run([sys.executable, script])
    
    end_script = time.time()
    
    if result.returncode != 0:
        print(f"\n ERROR  al ejecutar {script}.")
        print("El pipeline se ha detenido para evitar datos corruptos.")
        sys.exit(result.returncode)
    
    print(f" {script} completado en {end_script - start_script:.2f} segundos.\n")

end_total = time.time()

print("===================================================")
print(f" Se finalizo el modelo :)")
print(f" Tiempo total: {end_total - start_total:.2f} segundos.")