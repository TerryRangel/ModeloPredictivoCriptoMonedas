import subprocess
import sys
import time

scripts = [
    "data_loader.py",              # 1. Descarga datos actualizados
    "regime_dataset_builder.py",   # 2. Calcula indicadores y regímenes 
    # OMITIMOS ml_regime_model.py para no reentrenar
    "trading_rules.py",            # 3. Genera las señales usando el modelo existente
    "backtesting_engine.py",
    "daily_trading_decision.py"    # 4. Muestra los resultados finales
]

print(" INICIANDO ACTUALIZACIÓN (SIN RE-ENTRENAR) ........")

start_total = time.time()

for script in scripts:
    print(f">>> Ejecutando: {script}...")
    start_script = time.time()
    
    result = subprocess.run([sys.executable, script])
    
    end_script = time.time()
    
    if result.returncode != 0:
        print(f"\n ERROR  al ejecutar {script}.")
        print("El pipeline se ha detenido.")
        sys.exit(result.returncode)
    
    print(f" {script} completado en {end_script - start_script:.2f} segundos.\n")

end_total = time.time()

print("===================================================")
print(f" Se actualizaron los datos exitosamente :)")
print(f" Tiempo total: {end_total - start_total:.2f} segundos.")
