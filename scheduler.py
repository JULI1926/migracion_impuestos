import schedule
import time
import subprocess
import os
from datetime import datetime

HOME    = os.path.expanduser("~")
PYTHON  = os.path.join(HOME, r"AppData\Local\Programs\Python\Python313\python.exe")
BASE    = os.path.join(HOME, r"Documents\migracion_impuestos")
LOGDIR  = os.path.join(HOME, r"Documents\Impuestos\Archivos_impuestos\Logs_tarea-programada")


def ejecutar():
    if datetime.now().weekday() == 0:  # 0 = lunes
        return

    os.makedirs(LOGDIR, exist_ok=True)
    fecha = datetime.now().strftime("%Y-%m-%d")
    log   = os.path.join(LOGDIR, f"tarea_{fecha}.txt")

    def log_msg(msg):
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")

    log_msg("Ejecutando procesamiento de RUTs...")
    with open(log, "a", encoding="utf-8") as f:
        subprocess.run([PYTHON, os.path.join(BASE, "procesar_ruts.py")], stdout=f, stderr=f)

    log_msg("Procesamiento finalizado. Ejecutando envio de correos...")
    with open(log, "a", encoding="utf-8") as f:
        subprocess.run([PYTHON, os.path.join(BASE, "envio_correo.py")], stdout=f, stderr=f)

    log_msg("Proceso terminado.")


schedule.every().day.at("13:00").do(ejecutar)

print(f"Scheduler iniciado. Próxima ejecución: {schedule.next_run()}")
while True:
    schedule.run_pending()
    time.sleep(30)
