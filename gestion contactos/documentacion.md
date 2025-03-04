# Documentación: Agenda de Contactos en Python con Tkinter

## 1. Estructura del código

La aplicación "Agenda de Contactos" está estructurada siguiendo un patrón de diseño funcional, donde cada componente del programa tiene una responsabilidad específica. El código está organizado en las siguientes secciones principales:

1. **Importaciones**: Módulos necesarios para el funcionamiento de la aplicación.
2. **Conexión a la base de datos**: Funciones para establecer y gestionar la conexión con MySQL.
3. **Validación de datos**: Funciones para validar la entrada del usuario.
4. **Operaciones CRUD**: Funciones para crear, leer, actualizar y eliminar contactos.
5. **Interfaz gráfica**: Configuración y elementos de la interfaz de usuario.
6. **Funcionalidades adicionales**: Exportación/importación de datos y modo oscuro.

Esta estructura modular facilita el mantenimiento y la extensión del código, permitiendo añadir nuevas funcionalidades sin afectar a las existentes.

## 2. Lógica de aplicación
La lógica de la aplicación se basa en la interacción con la base de datos MySQL para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre los contactos. La aplicación también incluye funcionalidades adicionales como exportar/importar datos y cambiar entre modos claro y oscuro.

## Explicación detallada de funciones

### Función de conexión a la base de datos
```python
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="contact_db"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al conectar a la base de datos: {err}")
        return None
```
**Descripción**: Establece la conexión con la base de datos MySQL.
**Parámetros**: No recibe parámetros.
**Retorno**: 
- Objeto de conexión si es exitosa
- None si falla la conexión
**Uso**: Se utiliza en todas las operaciones que requieren acceso a la base de datos.

### Funciones de validación

#### Validación de nombre
```python
def validate_name(name):
    if not name.strip():
        return "El campo 'Nombre' no puede estar vacío."
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return "El nombre solo debe contener letras y espacios."
    return ""
```
**Descripción**: Valida el formato del nombre ingresado.
**Parámetros**:
- `name` (str): Nombre a validar
**Retorno**: 
- String vacío si es válido
- Mensaje de error si no es válido
**Validaciones**:
- No puede estar vacío
- Solo puede contener letras y espacios

#### Validación de teléfono
```python
def validate_phone(phone):
    if not phone.strip():
        return "El campo 'Teléfono' no puede estar vacío."
    if not re.match(r'^\d{7,15}$', phone):
        return "El número de teléfono debe tener entre 7 y 15 dígitos."
    return ""
```
**Descripción**: Valida el formato del número de teléfono.
**Parámetros**:
- `phone` (str): Número de teléfono a validar
**Retorno**: 
- String vacío si es válido
- Mensaje de error si no es válido
**Validaciones**:
- No puede estar vacío
- Debe tener entre 7 y 15 dígitos

#### Validación de email
```python
def validate_email(email):
    if not email.strip():
        return "El campo 'Email' no puede estar vacío."
    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return "El formato del correo electrónico es inválido."
    
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        selected_item = tree.selection()
        if selected_item:
            current_id = tree.item(selected_item)['values'][0]
            query = "SELECT COUNT(*) FROM contacts WHERE email = %s AND id != %s"
            cursor.execute(query, (email, current_id))
        else:
            query = "SELECT COUNT(*) FROM contacts WHERE email = %s"
            cursor.execute(query, (email,))
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        if count > 0:
            return "Este correo electrónico ya está registrado en la base de datos."
    return ""
```
**Descripción**: Valida el formato del email y su unicidad en la base de datos.
**Parámetros**:
- `email` (str): Correo electrónico a validar
**Retorno**: 
- String vacío si es válido
- Mensaje de error si no es válido
**Validaciones**:
- No puede estar vacío
- Debe tener formato válido de email
- No puede estar duplicado en la base de datos

### Funciones CRUD

Las funciones CRUD (Create, Read, Update, Delete) son las operaciones fundamentales para gestionar los contactos en la base de datos. Estas funciones permiten:

- Crear nuevos contactos (Create)
- Leer/consultar contactos existentes (Read) 
- Actualizar información de contactos (Update)
- Eliminar contactos (Delete)

Cada operación está implementada como una función independiente que interactúa con la base de datos MySQL mientras mantiene la consistencia e integridad de los datos.

#### Agregar contacto
```python
def add_contact():
    name = entry_name.get()
    phone = entry_phone.get()
    email = entry_email.get()

    name_error = validate_name(name)
    phone_error = validate_phone(phone)
    email_error = validate_email(email)

    if name_error or phone_error or email_error:
        messagebox.showerror("Error", "\n".join([name_error, phone_error, email_error]))
        return

    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        query = "INSERT INTO contacts (name, phone, email) VALUES (%s, %s, %s)"
        values = (name, phone, email)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        messagebox.showinfo("Éxito", "Contacto agregado correctamente.")
        entry_name.delete(0, tk.END)
        entry_phone.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        refresh_table()
```
**Descripción**: Agrega un nuevo contacto a la base de datos.
**Parámetros**: No recibe parámetros directamente (usa valores de los campos de entrada).
**Proceso**:
1. Obtiene valores de los campos
2. Valida los datos
3. Inserta en la base de datos
4. Limpia los campos
5. Actualiza la tabla

#### Actualizar contacto
```python
def update_contact():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Selecciona un contacto para actualizar.")
        return

    contact_id = tree.item(selected_item)['values'][0]
    name = entry_name.get()
    phone = entry_phone.get()
    email = entry_email.get()

    name_error = validate_name(name)
    phone_error = validate_phone(phone)
    email_error = validate_email(email)

    if name_error or phone_error or email_error:
        messagebox.showerror("Error", "\n".join([name_error, phone_error, email_error]))
        return

    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        query = "UPDATE contacts SET name=%s, phone=%s, email=%s WHERE id=%s"
        values = (name, phone, email, contact_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        messagebox.showinfo("Éxito", "Contacto actualizado correctamente.")
        refresh_table()
```
**Descripción**: Actualiza un contacto existente.
**Parámetros**: No recibe parámetros directamente (usa valores de los campos y selección).
**Proceso**:
1. Verifica selección de contacto
2. Obtiene valores actualizados
3. Valida los datos
4. Actualiza en la base de datos
5. Actualiza la tabla

#### Eliminar contacto
```python
def delete_contact():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Selecciona un contacto para eliminar.")
        return

    confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este contacto?")
    if not confirm:
        return

    contact_id = tree.item(selected_item)['values'][0]
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        query = "DELETE FROM contacts WHERE id=%s"
        values = (contact_id,)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        messagebox.showinfo("Éxito", "Contacto eliminado correctamente.")
        refresh_table()
        entry_name.delete(0, tk.END)
        entry_phone.delete(0, tk.END)
        entry_email.delete(0, tk.END)
```
**Descripción**: Elimina un contacto de la base de datos.
**Parámetros**: No recibe parámetros directamente (usa selección de tabla).
**Proceso**:
1. Verifica selección de contacto
2. Pide confirmación
3. Elimina de la base de datos
4. Limpia campos
5. Actualiza la tabla

#### Refrescar tabla
```python
def refresh_table():
    for item in tree.get_children():
        tree.delete(item)

    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM contacts"
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=(row['id'], row['name'], row['phone'], row['email']))
        cursor.close()
        connection.close()
```
**Descripción**: Actualiza la visualización de la tabla de contactos.
**Parámetros**: No recibe parámetros.
**Proceso**:
1. Limpia la tabla actual
2. Obtiene todos los contactos
3. Inserta cada contacto en la tabla

#### Búsqueda de contactos
```python
def search_contacts(event=None):
    search_text = entry_search.get().strip()
    for item in tree.get_children():
        tree.delete(item)

    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM contacts WHERE name LIKE %s OR phone LIKE %s OR email LIKE %s"
        values = (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%")
        cursor.execute(query, values)
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=(row['id'], row['name'], row['phone'], row['email']))
        cursor.close()
        connection.close()
```
**Descripción**: Realiza búsqueda en tiempo real de contactos.
**Parámetros**:
- `event`: Evento de teclado (opcional)
**Proceso**:
1. Obtiene texto de búsqueda
2. Busca coincidencias en nombre, teléfono y email
3. Actualiza la tabla con resultados

## 3. Interfaz gráfica y usabilidad (Tkinter)

La interfaz gráfica se construye utilizando Tkinter, la biblioteca estándar de Python para crear interfaces gráficas. Los principales componentes de la interfaz son:

### Ventana principal

```python
root = tk.Tk()
root.title("Agenda de Contactos")
root.geometry("800x600")
root.configure(bg="#F0F0F0")
```

La ventana principal tiene un tamaño de 800x600 píxeles y un fondo claro (#F0F0F0).

### Estilos personalizados

```python
style = ttk.Style()
style.theme_use("default")
style.configure("TLabel", background="#F0F0F0", font=("Arial", 12))
style.configure("TButton", padding=8, font=("Arial", 12), background="#007ACC", foreground="white")
```

Se utilizan estilos personalizados para mejorar la apariencia de los elementos de la interfaz, como etiquetas, botones y la tabla de contactos.

### Campos de entrada

La aplicación incluye campos de entrada para:
- Búsqueda de contactos
- Nombre del contacto
- Número de teléfono
- Correo electrónico

Cada campo tiene una etiqueta asociada y está configurado con un tamaño y fuente específicos.

### Botones de acción

Los botones principales son:
- Agregar Contacto
```python
btn_add = ttk.Button(frame, text="Agregar Contacto", command=add_contact)
btn_add.grid(row=4, column=0, padx=5, pady=10)
```
- Actualizar Contacto
```python
btn_update = ttk.Button(frame, text="Actualizar Contacto", command=update_contact)
btn_update.grid(row=4, column=1, padx=5, pady=10)
```

- Eliminar Contacto
```python
btn_delete = ttk.Button(frame, text="Eliminar Contacto", command=delete_contact)
btn_delete.grid(row=4, column=2, padx=5, pady=10)
```

- Exportar CSV
```python
btn_export = ttk.Button(frame, text="Exportar CSV", command=export_contacts)
btn_export.grid(row=4, column=3, padx=5, pady=10)
```

- Importar CSV
```python
btn_import = ttk.Button(frame, text="Importar CSV", command=import_contacts)
btn_import.grid(row=4, column=4, padx=5, pady=10)
```

- Cambiar tema (modo claro/oscuro)
```python
btn_theme = ttk.Button(frame, text="🌙 Modo Oscuro", command=toggle_dark_mode)
btn_theme.grid(row=0, column=3, padx=5, pady=5)
```
Estos botones están dispuestos en una fila para facilitar su acceso.

### Tabla de contactos

```python
tree = ttk.Treeview(frame, columns=("ID", "Nombre", "Teléfono", "Correo"), show="headings", height=15)
```

La tabla de contactos se implementa utilizando un widget Treeview, que muestra los contactos en columnas para ID, Nombre, Teléfono y Correo. La tabla incluye una barra de desplazamiento vertical para navegar por los contactos cuando hay muchos.

### Interactividad

La interfaz es interactiva, permitiendo:
- Seleccionar contactos de la tabla para editarlos o eliminarlos
- Buscar contactos en tiempo real mientras se escribe
- Recibir feedback visual mediante mensajes emergentes
- Cambiar entre modos claro y oscuro

## 4. Funcionalidades adicionales

### Exportación e importación de contactos

La aplicación permite exportar los contactos a un archivo CSV e importarlos desde un archivo CSV. Estas funciones son útiles para:
- Hacer copias de seguridad de los contactos
- Transferir contactos entre diferentes instalaciones de la aplicación
- Importar contactos desde otras aplicaciones

```python
def export_contacts():
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM contacts")
            rows = cursor.fetchall()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", "*.csv")]
            )
            
            if file_path:
                with open(file_path, 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=['name', 'phone', 'email'])
                    writer.writeheader()
                    for row in rows:
                        writer.writerow({
                            'name': row['name'],
                            'phone': row['phone'],
                            'email': row['email']
                        })
                messagebox.showinfo("Éxito", "Contactos exportados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
        finally:
            cursor.close()
            connection.close()
```

La función `export_contacts()` recupera todos los contactos de la base de datos, solicita al usuario una ubicación para guardar el archivo CSV y escribe los datos en ese archivo.

```python
def import_contacts():
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )
    
    if file_path:
        connection = create_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                with open(file_path, 'r') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        query = "INSERT INTO contacts (name, phone, email) VALUES (%s, %s, %s)"
                        cursor.execute(query, (row['name'], row['phone'], row['email']))
                connection.commit()
                messagebox.showinfo("Éxito", "Contactos importados correctamente")
                refresh_table()
            except Exception as e:
                messagebox.showerror("Error", f"Error al importar: {str(e)}")
            finally:
                cursor.close()
                connection.close()
```

La función `import_contacts()` solicita al usuario seleccionar un archivo CSV, lee los datos del archivo y los inserta en la base de datos.

### Modo oscuro

```python
def toggle_dark_mode():
    current_bg = root.cget("bg")
    if current_bg == "#F0F0F0":  # Light mode
        # Dark mode colors
        root.configure(bg="#2B2B2B")
        frame.configure(bg="#2B2B2B")
        style.configure("TLabel", background="#2B2B2B", foreground="white")
        style.configure("TButton", background="#007ACC", foreground="white")
        style.configure("Treeview", background="#3C3F41", foreground="white", fieldbackground="#3C3F41")
        style.configure("Treeview.Heading", background="#007ACC", foreground="white")
        btn_theme.configure(text="☀️ Modo Claro")
    else:  # Dark mode
        # Light mode colors
        root.configure(bg="#F0F0F0")
        frame.configure(bg="#F0F0F0")
        style.configure("TLabel", background="#F0F0F0", foreground="black")
        style.configure("TButton", background="#007ACC", foreground="white")
        style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
        style.configure("Treeview.Heading", background="#007ACC", foreground="white")
        btn_theme.configure(text="🌙 Modo Oscuro")
```

La función `toggle_dark_mode()` cambia los colores de la interfaz entre un tema claro y uno oscuro, mejorando la accesibilidad y permitiendo a los usuarios personalizar la apariencia de la aplicación según sus preferencias.

## 5. Documentación, comentarios y uso de asistentes de código basados en IA

El código está bien documentado con comentarios que explican el propósito de cada función y sección importante. Los comentarios siguen un estilo consistente y proporcionan información útil para entender el funcionamiento del código.

Ejemplos de comentarios:

```python
# Configuración de la conexión a la base de datos MySQL
def create_db_connection():
    # ...

# Función para validar el nombre
def validate_name(name):
    # ...

# Función para agregar un contacto
def add_contact():
    # ...
```

Además, se han utilizado asistentes de código basados en IA para mejorar la calidad del código y añadir funcionalidades adicionales, como la exportación e importación de contactos y el modo oscuro.

## 6. Bibliografía

Para el desarrollo de esta aplicación, se han utilizado las siguientes tecnologías y recursos:

1. **Tkinter**: Biblioteca para la interfaz gráfica.
   - [Documentación de Tkinter](https://docs.python.org/3/library/tkinter.html)

2. **MySQL Connector**: Para la conexión con la base de datos MySQL.
   - [MySQL Connector/Python Documentation](https://www.w3schools.com/python/python_mysql_getstarted.asp)

3. **Expresiones regulares**: Para la validación de datos.
   - [Módulo re de Python](https://codingornot.com/08-python-validar-entradas-ejemplos)

4. **CSV**: Para la exportación e importación de datos.
   - [Módulo csv de Python](https://docs.python.org/3/library/csv.html)

## 7. Conclusiones y opiniones personales

La aplicación "Agenda de Contactos" es una herramienta útil para gestionar contactos personales o profesionales. Su interfaz intuitiva y sus funcionalidades adicionales la hacen adecuada para usuarios con diferentes niveles de experiencia.

Puntos fuertes:
- Interfaz gráfica intuitiva y atractiva
- Validación robusta de datos
- Funcionalidades de búsqueda en tiempo real
- Exportación e importación de contactos
- Modo oscuro para mejorar la accesibilidad

Áreas de mejora:
- Añadir más campos para los contactos (dirección, fecha de nacimiento, etc.)
- Implementar grupos de contactos
- Añadir funcionalidades de respaldo automático
- Mejorar la seguridad de la conexión a la base de datos

## 8. Aspectos innovadores más allá de requisitos

La aplicación incluye varias características innovadoras que van más allá de los requisitos básicos de una agenda de contactos:

1. **Modo oscuro**: Mejora la accesibilidad y reduce la fatiga visual en entornos con poca luz.

2. **Exportación e importación de contactos**: Facilita la transferencia de datos entre diferentes instalaciones o aplicaciones.

3. **Validación en tiempo real**: Proporciona feedback inmediato al usuario sobre la validez de los datos introducidos.

4. **Búsqueda dinámica**: Permite encontrar contactos rápidamente mientras se escribe.

5. **Interfaz responsiva**: Los elementos de la interfaz se adaptan al tamaño de la ventana.

Estas características mejoran significativamente la experiencia del usuario y hacen que la aplicación sea más útil y agradable de usar.