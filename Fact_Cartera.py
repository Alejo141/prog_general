import streamlit as st
import pandas as pd
from io import BytesIO
import os

# Configuración inicial de la página
st.set_page_config(page_title="Captura de datos - Facturación y Cartera", page_icon="📂", layout="centered")
st.title("📂 Captura de datos por columna")

# Menú de selección
opcion = st.radio("Selecciona el tipo de captura de datos:", ("Facturación", "Cartera"))

# Función para procesar archivos de Facturación
def procesar_facturacion(file):
    df = pd.read_excel(file)
    columnas_deseadas = ["nfacturasiigo", "nui", "identificacion", "address", "localidad", 
                         "cantidad", "fechaemi", "p_inicial", "p_final", "mes", "ano"]
    df_filtrado = df[columnas_deseadas]

    # Eliminar guiones en "nfacturasiigo" y "nui"
    df_filtrado["nfacturasiigo"] = df_filtrado["nfacturasiigo"].astype(str).str.replace("-", "", regex=True)
    df_filtrado["nui"] = df_filtrado["nui"].astype(str).str.replace("-", "", regex=True)

    # Formatear fechas
    df_filtrado["fechaemi"] = pd.to_datetime(df_filtrado["fechaemi"], errors='coerce').dt.strftime('%Y-%m-%d')
    df_filtrado["p_inicial"] = pd.to_datetime(df_filtrado["p_inicial"], errors='coerce').dt.strftime('%Y-%m-%d')
    df_filtrado["p_final"] = pd.to_datetime(df_filtrado["p_final"], errors='coerce').dt.strftime('%Y-%m-%d')

    # Convertir a mayúsculas
    df_filtrado["address"] = df_filtrado["address"].astype(str).str.upper()
    df_filtrado["localidad"] = df_filtrado["localidad"].astype(str).str.upper()

    return df_filtrado

# Función para procesar archivos de Cartera
def procesar_cartera(file, nombre_archivo):
    df = pd.read_excel(file)
    columnas_deseadas = ["Identificación", "NUI", "Factura", "Centro de costo", "Saldo Factura", "Mes de Cobro"]
    
    # Filtrar columnas existentes
    columnas_presentes = [col for col in columnas_deseadas if col in df.columns]
    df_filtrado = df[columnas_presentes]

    # Eliminar guiones en "NUI" y "Factura"
    if "NUI" in df_filtrado.columns:
        df_filtrado["NUI"] = df_filtrado["NUI"].astype(str).str.replace("-", "", regex=True)
    if "Factura" in df_filtrado.columns:
        df_filtrado["Factura"] = df_filtrado["Factura"].astype(str).str.replace("-", "", regex=True)

    # Convertir "Centro de costo" a mayúsculas
    if "Centro de costo" in df_filtrado.columns:
        df_filtrado["Centro de costo"] = df_filtrado["Centro de costo"].astype(str).str.upper()

    # Reemplazar valores nulos con "NA"
    df_filtrado.fillna("NA", inplace=True)

    # Filtrar filas donde "Factura" esté vacía
    if "Factura" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["Factura"] != "NA"]

    # Procesar "Mes de Cobro"
    if "Mes de Cobro" in df_filtrado.columns:
        df_filtrado["Mes de Cobro"] = df_filtrado["Mes de Cobro"].astype(str)
        df_filtrado[["mes", "año"]] = df_filtrado["Mes de Cobro"].str.split(" ", expand=True).fillna("")

        meses_dict = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
            "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }

        df_filtrado["mes"] = df_filtrado["mes"].str.lower().map(meses_dict)
        df_filtrado["año"] = pd.to_numeric(df_filtrado["año"], errors='coerce')

    # Agregar nombre del archivo
    df_filtrado.insert(0, "nombre_archivo", nombre_archivo)

    return df_filtrado

# Función para generar archivo Excel
def generar_xlsx(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return output

# Función para generar archivo CSV
def generar_csv(df):
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output

# Subida de archivo según la opción seleccionada
archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

if archivo is not None:
    if opcion == "Facturación":
        df_filtrado = procesar_facturacion(archivo)
    else:  # Cartera
        df_filtrado = procesar_cartera(archivo, archivo.name)

    st.success("Archivo procesado correctamente.")
    st.dataframe(df_filtrado)

    # Descarga en Excel
    xlsx = generar_xlsx(df_filtrado)
    nombre_salida_xlsx = os.path.splitext(archivo.name)[0] + ".xlsx"
    st.download_button(label="📥 Descargar Excel", data=xlsx, file_name=nombre_salida_xlsx, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Descarga en CSV
    csv = generar_csv(df_filtrado)
    nombre_salida_csv = os.path.splitext(archivo.name)[0] + ".csv"
    st.download_button(label="📥 Descargar CSV", data=csv, file_name=nombre_salida_csv, mime="text/csv")
