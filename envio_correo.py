import psycopg2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from collections import defaultdict

# Configuración de la base de datos
db_config = {
    'host': '40.121.222.132',
    'user': 'postgres',
    'password': 'y6?/s,Z;aN{A6USb',
    'database': 'Impuestos'
}

# Configuración del correo
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'soporteyawi@cyt.com.co'
smtp_password = 'ratw sbrv tncc bbgr'


# Consulta a la base de datos
def ejecutar_consulta(query):
    conexion = psycopg2.connect(**db_config)
    cursor = conexion.cursor()
    cursor.execute(query)
    columnas = [desc[0] for desc in cursor.description]
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return columnas, resultados


consultas = [
    {"titulo": "Gran Contribuyentes", "sql": """SELECT ob.cod_obligacion::integer, ob.obligacion, ob.cod_impuesto , obligcliente."NumeroRut", obligcliente.valor, obligcliente."Nombre", obligcliente."Tipo_Contribuyente" , calendario.digito, calendario.fecha_limite, calendario.tipo_impuesto, calendario.observacion , cc.correo  
FROM obligaciones_trib ob    
JOIN (  	select x."Nombre", x."NumeroRut", x.valor::integer, x."Tipo_Contribuyente" 
	  from (  	SELECT x."Nombre", x."NumeroRut", split_part(x.responsabilidades, chr(10), 1) AS valor, x."Tipo_Contribuyente"  	
			FROM (  		SELECT clientes_1."Nombre", clientes_1."NumeroRut" 		, unnest(string_to_array(clientes_1."Responsabilidades"::text, ' '::text)) AS responsabilidades, clientes_1."Tipo_Contribuyente" FROM clientes clientes_1) x 		) x where x.valor not in ('','as',CHR(13),'ón','os') ) obligcliente ON ob.cod_obligacion::integer = obligcliente.valor::integer  
			JOIN calendario  ON "substring"(obligcliente."NumeroRut"::text,9,10) = calendario.digito::text AND ob.cod_impuesto::integer = calendario.tipo_impuesto::integer   join "prueba-correo" cc  on obligcliente."NumeroRut"::integer = cc."nit"    where obligcliente."Tipo_Contribuyente" = 'Gran Contribuyente' and calendario."fecha_limite" >= current_date and (calendario."fecha_limite"-current_date)=35 and ob.cod_impuesto <> '36' and ob.cod_obligacion not in ('48')"""},
    
    {"titulo": "Personas Jurídicas", "sql": """SELECT ob.cod_obligacion::integer, ob.obligacion, ob.cod_impuesto , obligcliente."NumeroRut", obligcliente.valor, obligcliente."Nombre", obligcliente."Tipo_Contribuyente" , calendario.digito, calendario.fecha_limite, calendario.tipo_impuesto, calendario.observacion , cc.correo 
FROM obligaciones_trib ob    
JOIN (  	select x."Nombre", x."NumeroRut", x.valor::integer, x."Tipo_Contribuyente" 
	  from (SELECT x."Nombre", x."NumeroRut", split_part(x.responsabilidades, chr(10), 1) AS valor, x."Tipo_Contribuyente"  	
			FROM (SELECT clientes_1."Nombre", clientes_1."NumeroRut" 		, unnest(string_to_array(clientes_1."Responsabilidades"::text, ' '::text)) AS responsabilidades, clientes_1."Tipo_Contribuyente" FROM clientes clientes_1) x 		) x where x.valor not in ('','as',CHR(13),'ón','os') ) obligcliente ON ob.cod_obligacion::integer = obligcliente.valor::integer  
JOIN calendario  ON "substring"(obligcliente."NumeroRut"::text,9,10) = calendario.digito::text AND ob.cod_impuesto::integer = calendario.tipo_impuesto::integer   
join "prueba-correo" cc  on obligcliente."NumeroRut"::integer = cc."nit"  
where obligcliente."Tipo_Contribuyente" <> 'Gran Contribuyente' 
and calendario."fecha_limite" >= current_date 
and (calendario."fecha_limite"-current_date)=35 
and ob.cod_obligacion not in ('41','14','48') 
and calendario.observacion <> 'Personas naturales' 
and ob.cod_impuesto <> '13'"""},
    
    {"titulo": "IVA", "sql": """SELECT ob.cod_obligacion::integer, ob.obligacion, ob.cod_impuesto , obligcliente."NumeroRut", obligcliente.valor, obligcliente."Nombre" , calendario.digito, calendario.fecha_limite, calendario.tipo_impuesto, calendario.observacion , cc.correo , iva."NIT", iva."IVA" 
FROM obligaciones_trib ob    
JOIN (  	select x."Nombre", x."NumeroRut", x.valor::integer 
	from (  	SELECT x."Nombre", x."NumeroRut", split_part(x.responsabilidades, chr(10), 1) AS valor  	
		FROM (  		SELECT clientes_1."Nombre", clientes_1."NumeroRut", unnest(string_to_array(clientes_1."Responsabilidades"::text, ' '::text)) AS responsabilidades FROM clientes clientes_1) x 		
	) x where x.valor not in ('','as',CHR(13),'ón','os') ) obligcliente 
ON ob.cod_obligacion::integer = obligcliente.valor::integer  
JOIN calendario  ON "substring"(obligcliente."NumeroRut"::text, 9,10) = calendario.digito::text AND ob.cod_impuesto::integer = calendario.tipo_impuesto::integer   
join "prueba-correo" cc  on obligcliente."NumeroRut"::integer = cc."nit"  
join (select "NIT", "IVA" from iva) iva 
	on iva."NIT"::integer = obligcliente."NumeroRut"::integer 
	and calendario.tipo_impuesto::text = iva."IVA" 
where calendario."fecha_limite" >= current_date 
and (calendario."fecha_limite"-current_date)=35  
and ob.cod_obligacion = '48'"""},
]


def registrar_log(nombre, rut, fecha, dato):
    with open("log_envios.txt", "a", encoding="utf-8") as f:
        f.write(f"{nombre} ({rut}) - {fecha} - {dato}\n")


def obtener_obligaciones_por_contribuyente():
    contribuyentes = defaultdict(lambda: defaultdict(list))
    for consulta in consultas:
        columnas, filas = ejecutar_consulta(consulta["sql"])
        for fila in filas:
            datos = dict(zip(columnas, fila))
            rut = datos.get("NumeroRut")
            nombre = datos.get("Nombre")
            fecha = datos.get("fecha_limite")
            correo = next((datos.get(c) for c in ['correo_4', 'correo_3', 'correo_2', 'correo_1', 'correo'] if datos.get(c)), None)

            if rut and nombre and fecha and correo:
                clave = (rut, nombre, correo)
                contribuyentes[clave][fecha].append(datos)
    return contribuyentes


def generar_mensaje_contribuyente(nombre, rut, obligaciones_por_fecha):
    cuerpo = f"<p>Señores:<br><strong>{nombre}</strong></p>"

    for fecha, obligaciones in obligaciones_por_fecha.items():
        lista_obligaciones = "<br>" + "<br>".join(f"- {ob.get('obligacion')}" for ob in obligaciones)
        cuerpo += f"<p>El próximo <strong>{fecha}</strong> se vence el plazo para la presentación de:<br><strong>{lista_obligaciones}</strong>.</p>"

    cuerpo += """
    <p>Les recordamos la importancia de enviar los soportes con la debida antelación para nuestra revisión y proceso de firma por parte del Revisor Fiscal encargado, de acuerdo a nuestra política son dos días hábiles antes de la fecha máxima de presentación, esto con el fin de evitar inconvenientes ante la DIAN al presentarlas el mismo día del vencimiento.</p>

    <p>Solicitamos que una vez se encuentre el borrador en la plataforma de la DIAN, nos informen por este medio para proceder a la firma en tiempo oportuno.</p>
    <p>Igualmente, una vez realizada la presentación y pago, agradecemos el envío de los soportes correspondientes.</p>
    <p>Si ya nos remitieron la información, por favor hacer caso omiso al presente correo.</p>
    <p style="text-align:center;"><strong><em>Por favor no responda a este correo, su contenido es un mensaje automático generado por nuestro sistema.</em></strong></p>
    <br><img src="http://drive.google.com/uc?export=view&id=1X7S0YuH9C1d7Y6KM9QDVm8fQl_avtKpf" width="80%">
    """
    return f"<html><body>{cuerpo}</body></html>"


def enviar_correo_individual(destinatario, asunto, cuerpo_html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = asunto
    msg['From'] = smtp_user
    msg['To'] = destinatario
    msg.attach(MIMEText(cuerpo_html, 'html'))
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, destinatario, msg.as_string())


def enviar_correos_por_contribuyente():
    agrupados = obtener_obligaciones_por_contribuyente()
    for (rut, nombre, correo), obligaciones_por_fecha in agrupados.items():
        html = generar_mensaje_contribuyente(nombre, rut, obligaciones_por_fecha)
        enviar_correo_individual(correo, "Recordatorio vencimiento de Impuestos", html)
        registrar_log(nombre, rut, "Correo enviado", correo)


# Ejecutar
enviar_correos_por_contribuyente()
