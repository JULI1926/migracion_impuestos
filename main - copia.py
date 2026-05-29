import os
import re
import pdfplumber

# if __name__ == "__main__":
   
#    ruta_ruts = r"C:\Users\Usuario\Documents\Impuestos\Archivos_impuestos\RUTS\AGROINDUSTRIA.pdf"
#    with pdfplumber.open(ruta_ruts) as pdf:
#        text = pdf.pages[0].extract_text()
       
#    print(text)
#    #nit = re.search(r"(.+)impuestos\s*y\s*aduanas", text,re.I)
#    nit = re.search(r"buz[óo]n\s*electr[óo]nic[oa]([\s]*[\d\s]*)", text,re.I)
#    nit_valor = nit.group(1).strip() if nit else "No encontrado"
#    nit_valor = nit_valor.replace(" ","")[:-1]
#    razon_social = re.search(r"Raz[óo]n\s+social\s*\n*(.+)", text)
#    razon_valor = razon_social.group(1).strip() if razon_social else "No encontrado"
#    responsabilidades = re.findall(r"53\.\s*c[óo]digo\s*[\d\s]+\s(.+)obligados\s*aduaneros", text,re.I|re.DOTALL)
#    responsabilidades_valor = responsabilidades[0] if responsabilidades else "No encontrado"
#    print(nit_valor)


ruta_ruts = r"C:\Users\Usuario\Documents\Impuestos\Archivos_impuestos\RUTS"

def extraer_info_rut(pdf_path):
    """Extrae NIT, Razón Social y Responsabilidades de un archivo PDF RUT."""
   
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()

    nit = re.search(r"buz[óo]n\s*electr[óo]nic[oa]([\s]*[\d\s]*)", text,re.I)
    nit_valor = nit.group(1).strip() if nit else "No encontrado"
    nit_valor = nit_valor.replace(" ","")[:-1]
    razon_social = re.search(r"Raz[óo]n\s+social\s*\n*(.+)", text)
    razon_valor = razon_social.group(1).strip() if razon_social else "No encontrado"
    responsabilidades = re.findall(r"53\.\s*c[óo]digo\s*[\d\s]+\s(.+)obligados\s*aduaneros", text,re.I|re.DOTALL)
    responsabilidades_valor = responsabilidades[0] if responsabilidades else "No encontrado"

    

    print(f"\n📄 Archivo: {os.path.basename(pdf_path)}")
    print(f"🆔 NIT: {nit_valor}")
    print(f"🏢 Razón Social / Nombre: {razon_valor}")

    if responsabilidades:
        print("📋 Responsabilidades, Calidades y Atributos:")
        print(f"{responsabilidades_valor}")
        # for codigo, desc in responsabilidades:
        #     print(f"   - {codigo}: {desc.strip()}")
    else:
        print("📋 No se encontraron responsabilidades registradas.")


def procesar_ruts_en_carpeta(ruta):
    """Procesa todos los PDFs en la carpeta especificada."""
    print(f"\n🔎 Buscando archivos PDF en: {ruta}\n")
    for archivo in os.listdir(ruta):
        if archivo.lower().endswith(".pdf"):
            pdf_path = os.path.join(ruta, archivo)
            extraer_info_rut(pdf_path)


if __name__ == "__main__":
    procesar_ruts_en_carpeta(ruta_ruts)



 
   
