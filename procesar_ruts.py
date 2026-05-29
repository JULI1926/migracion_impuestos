import os 
import re
import pdfplumber
import psycopg2
import shutil
from datetime import datetime


_HOME        = os.path.expanduser("~")
DATA_BASE    = os.path.join(_HOME, r"Documents\Impuestos")
RUTA_ENTRADA = os.path.join(DATA_BASE, r"Archivos_impuestos\RUTS-Nuevos")
RUTA_SALIDA  = os.path.join(DATA_BASE, r"Archivos_impuestos\RUTS")
RUTA_LOGS    = os.path.join(DATA_BASE, r"Archivos_impuestos\Logs")

db_config = {
    'host': '40.121.222.132',
    'user': 'postgres',
    'password': 'y6?/s,Z;aN{A6USb',
    'database': 'Impuestos'
}

# Crear carpeta Logs si no existe
os.makedirs(RUTA_LOGS, exist_ok=True)

# Nombre del log diario
fecha_hoy = datetime.now().strftime("%Y-%m-%d")
LOG_PATH = os.path.join(RUTA_LOGS, f"errores ({fecha_hoy}).txt")

# FUNCIONES DE LOG

def escribir_log(mensaje):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")


# VALIDAR SI NIT YA EXISTE

def nit_existe(numero_rut):
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        sql = 'SELECT 1 FROM prueba WHERE "NumeroRut" = %s LIMIT 1'
        cur.execute(sql, (numero_rut,))
        existe = cur.fetchone() is not None

        cur.close()
        conn.close()
        return existe

    except Exception as e:
        escribir_log(f"Error verificando duplicado NIT {numero_rut}: {e}")
        return False

# INSERCIÓN EN BD

def insertar_en_bd(nombre, numero_rut, responsabilidades):
    # Validación de duplicados
    if nit_existe(numero_rut):
        mensaje = f"NIT duplicado, no insertado: {numero_rut} - {nombre}"
        print(mensaje)
        escribir_log(mensaje)
        return  # No insertamos nada

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        sql = """
            INSERT INTO prueba ("Nombre", "NumeroRut", "Responsabilidades")
            VALUES (%s, %s, %s)
        """

        cur.execute(sql, (nombre, numero_rut, responsabilidades))
        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        mensaje = f"Error insertando en BD para NIT {numero_rut}: {e}"
        print(mensaje)
        escribir_log(mensaje)


# EXTRACCIÓN DEL PDF


def extraer_info_rut(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto = pdf.pages[0].extract_text()

    nit = re.search(r"buz[óo]n\s*electr[óo]nic[oa]([\s]*[\d\s]*)", texto, re.I)
    numero_rut = nit.group(1).strip().replace(" ", "")[:-1] if nit else ""

    razon_social = re.search(r"Raz[oó]n\s+social\s*\n*(.+)", texto, re.I)
    nombre = razon_social.group(1).strip() if razon_social else ""

    seccion = re.search(
        r"Responsabilidades, Calidades y Atributos(.*?)IMPORTANTE",
        texto,
        re.S | re.I
    )

    bloque = seccion.group(1) if seccion else texto

    responsabilidades = re.findall(r"(\d{2,3})\s*[-]", bloque)
    responsabilidades = list(dict.fromkeys(responsabilidades))
    responsabilidades_str = " ".join(responsabilidades)

    print("\nArchivo:", os.path.basename(pdf_path))
    print("NIT:", numero_rut if numero_rut else "No encontrado")
    print("Nombre:", nombre if nombre else "No encontrado")
    print("Responsabilidades:", responsabilidades_str if responsabilidades_str else "No encontrado")
    print("---------------------------------------------")

    escribir_log(
        f"Procesado archivo {os.path.basename(pdf_path)} | "
        f"NIT: {numero_rut} | Nombre: {nombre} | Resp: {responsabilidades_str}"
    )

    return nombre, numero_rut, responsabilidades_str


# PROCESAR UN PDF

def procesar_pdf_unico(ruta_pdf):
    nombre, numero_rut, responsabilidades = extraer_info_rut(ruta_pdf)

    insertar_en_bd(nombre, numero_rut, responsabilidades)

    os.makedirs(RUTA_SALIDA, exist_ok=True)
    shutil.move(ruta_pdf, os.path.join(RUTA_SALIDA, os.path.basename(ruta_pdf)))

    print("Procesado:", os.path.basename(ruta_pdf))
    escribir_log(f"Archivo movido: {os.path.basename(ruta_pdf)}")


# PROCESAMIENTO

def procesar_ruts():
    archivos = [f for f in os.listdir(RUTA_ENTRADA) if f.lower().endswith(".pdf")]

    if not archivos:
        print("No se encontraron archivos nuevos.")
        escribir_log("No hay archivos nuevos para procesar.")
        return

    for archivo in archivos:
        ruta_pdf = os.path.join(RUTA_ENTRADA, archivo)
        procesar_pdf_unico(ruta_pdf)



if __name__ == "__main__":
    procesar_ruts()
