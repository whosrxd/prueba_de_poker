import streamlit as st
import pandas as pd
import scipy.stats as stats

# Configuración para pantalla completa
st.set_page_config(layout="wide")

st.title("Prueba de Póker")
st.divider()

# Función para realizar las operaciones
def multiplicador_constante(constante, semilla1, iteraciones):
    # Lista para almacenar los resultados
    resultados = []
    
    # Longitud de semilla
    longitud_semilla = len(str(semilla1))
    
    for i in range(iteraciones):
        # Calcula el producto de la semilla
        producto = semilla1 * constante
        longitud = len(str(producto))
        
        # Asegurándonos de que producto tenga 0 a la izquierda si es necesario
        if longitud <= 8:
            producto = f"{producto:08}"
        elif longitud <= 16:
            producto = f"{producto:016}"
        elif longitud <= 32:
            producto = f"{producto:032}"
        
        # Tomando los 4 dígitos de en medio según la longitud
        if longitud <= 8:
            medio = producto[2:6]
        elif longitud <= 16:
            medio = producto[6:10]
        elif longitud <= 32:
            medio = producto[14:18]
        
        # Convirtiendo a int()
        medio = int(medio)
        
        # Obteniendo ri
        ri = medio / 10**longitud_semilla
        
        # Guardamos los resultados en una lista
        resultados.append({
            'Semilla 1': semilla1,
            'Constante': constante,
            'Producto': producto,
            'Longitud': longitud,
            'Medio': medio,
            'ri': ri
        })
                
        # La nueva semilla será el valor de 'medio' calculado en esta iteración
        semilla1 = medio
        
    return resultados

# Lógica para navegar entre páginas
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"  # Página inicial por defecto
    
# Página inicial
if st.session_state.pagina == "inicio":
    # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
    col1, espacio, col2 = st.columns([2, 0.5, 3])

    with col1:
        st.header("1. Ingresa los datos")
        semilla_input = st.text_input("Ingresa tu semilla (número de dígitos pares y mayor a 0):")
        constante_input = st.text_input("Ingresa tu constante (número de dígitos pares y mayor a 0):")
        iteraciones_input = st.number_input("Ingresa las iteraciones:", min_value = 0, max_value = 30, step = 1)

    # Si ambos inputs están llenos, hacer las validaciones y mostrar los resultados
    if semilla_input and constante_input and iteraciones_input:
        try:
            semilla1 = int(semilla_input)  # Convertir la semilla a entero
            constante = int(constante_input)  # Convertir la semilla a entero
            iteraciones = int(iteraciones_input)  # Convertir las iteraciones a entero

            # Validación de las condiciones de entrada
            if semilla1 > 0 and len(str(semilla1)) % 2 == 0 and constante > 0 and len(str(constante)) % 2 == 0 and iteraciones > 0:
                # Obtener los resultados de las operaciones
                resultados = multiplicador_constante(constante, semilla1, iteraciones) 
                
                # Guardar los resultados en session_state para usarlos en otra página
                st.session_state.datos = resultados
                            
                # Mostrar la tabla en la columna derecha
                with col2:
                    st.header("Tabla Generada con Multiplicador Constante")
                                    
                    # Convertir la lista de diccionarios en un DataFrame
                    df = pd.DataFrame(resultados)
                    
                    # Asegurar 4 decimales reales y visuales
                    df['ri'] = df['ri'].astype(float).round(4)
                    df['ri'] = df['ri'].apply(lambda x: f"{x:.4f}")
            
                    df.index = df.index + 1
                    df = df.rename_axis("Iteración")
                    
                    st.dataframe(df, use_container_width = True)  
                    
                with col1:
                    st.divider()
                    st.header("2. Genera")
                    if st.button("Ir a Prueba de Póker"):
                        st.session_state.pagina = "Resolver"
                        st.rerun()  # Recarga la página               

            else:
                st.error("Recuerda que la semilla debe tener un número de dígitos pares y mayor a 0, y las iteraciones deben ser mayores a 0.")
        except ValueError:
            st.error("Por favor, ingresa valores numéricos válidos para la semilla y las iteraciones.")
            
# Página de resolución
elif st.session_state.pagina == "Resolver":
    # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
    col1, espacio, col2 = st.columns([2, 0.2, 3])
    
    if "resultados" in st.session_state:  # Verifica que los datos existan
        resultados = st.session_state.resultados

    if "datos" in st.session_state:  # Verifica que los datos existan
        datos = st.session_state["datos"]
    
        with col1:
            # Crear un DataFrame solo con la columna 'ri'
            df_ri = pd.DataFrame(datos)[['ri']]
            
            # Asegurar 4 decimales reales y visuales
            df_ri['ri'] = df_ri['ri'].astype(float).round(4)
            df_ri['ri'] = df_ri['ri'].apply(lambda x: f"{x:.4f}")
            
            # Mostrar la tabla con solo la columna 'ri'
            st.subheader("Números Pseudoaleatorios")
            df_ri.index += 1
            df = df_ri.rename_axis("Datos")
            
            st.dataframe(df, use_container_width = True)
            
        with col2:
            st.subheader("Ingreso de Datos")
            intervalo_de_cf = st.number_input("Ingrese el intervalo de confianza: ", min_value = 0, max_value = 100, step = 1)
            
            if intervalo_de_cf:
                
                # Alpha
                alpha = (100 - intervalo_de_cf) / 100
                
                # Grados de libertad
                grados_de_libertad = 5 - 1
               
                # Tabla 1
                # Inicializar el diccionario con los dígitos del 0 al 9
                conteo_digitos_total = {str(i): 0 for i in range(10)}

                # Crear una lista para almacenar los resultados de cada fila
                conteo_digitos_filas = []

                # Iterar sobre cada fila del DataFrame
                for index, row in df_ri.iterrows():
                    # Obtener el número decimal de la fila
                    valor = str(row['ri'])[2:]  # Aquí se omite la parte '0.' y solo tomamos los decimales
                    
                    # Inicializar el conteo por fila
                    conteo_fila = {str(i): 0 for i in range(10)}
                    
                    # Contar los dígitos de este número
                    for digito in valor:
                        if digito in conteo_fila:
                            conteo_fila[digito] += 1
                    
                    # Almacenar el conteo de esta fila en la lista
                    conteo_digitos_filas.append(conteo_fila)
                    
                    # Sumar al conteo total
                    for digito, count in conteo_fila.items():
                        conteo_digitos_total[digito] += count

                # Convertir los conteos por fila a un DataFrame para mostrarlo
                df_conteo = pd.DataFrame(conteo_digitos_filas)
                df_conteo.index += 1
                df_conteo = df_conteo.rename_axis("Datos")

                # Mostrar el DataFrame con los conteos de cada fila
                # st.dataframe(df_conteo, use_container_width=True)
                
                # Tabla 2
                
                # Lista de números que deseas contar
                numeros_a_contar = [2, 3, 4]

                # Crear una lista vacía para almacenar los conteos de cada número
                conteos = []

                # Iterar sobre las filas del DataFrame
                for index, row in df_conteo.iterrows():
                    conteo_fila = []
                    # Contar cuántas veces aparece cada número en la fila
                    for numero in numeros_a_contar:
                        conteo = row.values.tolist().count(numero)
                        conteo_fila.append(conteo)
                    conteos.append(conteo_fila)  # Agregar los conteos por fila

                # Crear un DataFrame con los conteos por cada número
                baraja = pd.DataFrame(conteos, columns=[f'Conteo de {numero}' for numero in numeros_a_contar])

                # Creando nueva columna y moviendola al principio
                baraja['TD'] = 4 - baraja['Conteo de 2'] - baraja['Conteo de 3'] - baraja['Conteo de 4']
                baraja.insert(0, 'TD', baraja.pop('TD'))
                
                baraja.index += 1
                baraja = baraja.rename_axis("Datos")

                # Mostrar el DataFrame con los conteos
                # st.dataframe(baraja, use_container_width = True) 
                
                # Tabla 3
                # Definir los encabezados de las columnas y las filas (índices)
                columnas = ['Probabilidad', 'Oi', 'Ei', '(Oi - Ei)^2 / Ei']
                filas = ['TD', '1P', '2P', 'T', 'P']

                # Crear un DataFrame vacío con las columnas y filas definidas
                df_vacio = pd.DataFrame(index=filas, columns=columnas)
                
                valores_probabilidad = [0.5040, 0.4320, 0.027, 0.036, 0.001]
                df_vacio['Probabilidad'] = valores_probabilidad
                
                # Calculando los valores observados
                juego = {
                    'TD': (baraja['TD'] == 4).sum(),
                    '1P': (baraja['Conteo de 2'] == 1).sum(),
                    '2P': (baraja['Conteo de 2'] == 2).sum(),
                    'T': (baraja['Conteo de 3'] == 1).sum(),
                    'P': (baraja['Conteo de 4'] == 1).sum()
                }

                # Asignar los conteos a la columna 'Oi' del DataFrame
                for clave, valor in juego.items():
                    df_vacio.loc[clave, 'Oi'] = valor
                    
                # Contar el total de números pseudoaleatorios
                n = len(df_ri)
                
                for clave, valor in juego.items():
                    df_vacio.loc[clave, 'Ei'] = valores_probabilidad[filas.index(clave)] * n
                
                # Calcular la última columna
                df_vacio['(Oi - Ei)^2 / Ei'] = ((df_vacio['Oi'] - df_vacio['Ei'])**2) / df_vacio['Ei']

                # Calcular la suma de la última columna
                estadistico = df_vacio['(Oi - Ei)^2 / Ei'].sum()
                
                # Nueva fila para el estadístico
                df_vacio.loc['Suma'] = ['', '', '', estadistico]          

                # Mostrar la tabla vacía en Streamlit
                st.subheader("Tabla de Prueba de Póker")
                st.dataframe(df_vacio, use_container_width=True)          
                
                # Muestra la imagen de la tabla Chi Cuadrada            
                st.image("chi_cuadrada.png", caption = "Tabla de Chi Cuadrada.")
                
                # Valor en tabla de chi cuadrada
                chi2_critico = stats.chi2.ppf(1 - alpha, grados_de_libertad)

                # Estadístico de chi cuadrada
                st.write(f"El estadístico en tabla de Prueba de Póker fue {estadistico  }")
                
                # Mostrar el valor crítico para referencia
                st.write(f"Valor crítico de chi-cuadrada: {chi2_critico}")

                # Ahora compara el valor calculado (chi_cuadrada) con el valor crítico
                if estadistico < chi2_critico:
                    st.success("Se acepta la hipótesis nula")
                else:
                    st.error("Hipótesis nula rechazada")
                    
    else:
        st.error("No hay datos disponibles. Regresa a la página principal.")

    with st.expander("Hecho por:"):
        st.write("Rodrigo González López S4A")
                
                