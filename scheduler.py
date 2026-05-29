import os
import subprocess
import sys
import time
from datetime import datetime

import schedule

PYTHON = sys.executable
BASE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
LOGDIR = os.path.join(HOME, r"Documents\Impuestos\Archivos_impuestos\Logs_tarea-programada")


def ejecutar():
    if datetime.now().weekday() == 0:  # 0 = lunes
        return

    os.makedirs(LOGDIR, exist_ok=True)
    fecha = datetime.now().strftime("%Y-%m-%d")
    log = os.path.join(LOGDIR, f"tarea_{fecha}.txt")

    def log_msg(msg):
        linea = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n"
        try:
            with open(log, "a", encoding="utf-8") as f:
                f.write(linea)
        except OSError as exc:
            print(f"No se pudo escribir en el log {log}: {exc}. Mensaje: {msg}")

    log_msg("Ejecutando procesamiento de RUTs...")
    with open(log, "a", encoding="utf-8") as f:
        subprocess.run(
            [PYTHON, os.path.join(BASE, "procesar_ruts.py")],
            stdout=f,
            stderr=f,
            cwd=BASE,
        )

    log_msg("Procesamiento finalizado. Ejecutando envio de correos...")
    with open(log, "a", encoding="utf-8") as f:
        subprocess.run(
            [PYTHON, os.path.join(BASE, "envio_correo.py")],
            stdout=f,
            stderr=f,
            cwd=BASE,
        )

    log_msg("Proceso terminado.")


# schedule.every().day.at("13:54").do(ejecutar)
schedule.every().day.at("11:45").do(ejecutar)

ahora = datetime.now()
proxima = schedule.next_run()
print(
    f"Scheduler iniciado. Hora actual: {ahora:%Y-%m-%d %H:%M:%S}. "
    f"Proxima ejecucion: {proxima:%Y-%m-%d %H:%M:%S}"
)

while True:
    schedule.run_pending()
    time.sleep(30)
