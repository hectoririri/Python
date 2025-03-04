import tkinter as tk
from tkinter import ttk
import mysql.connector
from tkinter import messagebox
import re
import csv
from tkinter import filedialog

# Configuración de la conexión a la base de datos MySQL
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Reemplaza con tu usuario
            password="",  # Reemplaza con tu contraseña
            database="contact_db"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al conectar a la base de datos: {err}")
        return None

# Función para validar el nombre
def validate_name(name):
    if not name.strip():
        return "El campo 'Nombre' no puede estar vacío."
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return "El nombre solo debe contener letras y espacios."
    return ""

# Función para validar el teléfono
def validate_phone(phone):
    if not phone.strip():
        return "El campo 'Teléfono' no puede estar vacío."
    if not re.match(r'^\d{7,15}$', phone):
        return "El número de teléfono debe tener entre 7 y 15 dígitos."
    return ""

# Función para validar el correo electrónico
def validate_email(email):
    # Verifica si el campo está vacío
    if not email.strip():
        return "El campo 'Email' no puede estar vacío."
    
    # Valida el formato del correo electrónico usando expresión regular
    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return "El formato del correo electrónico es inválido."
    
    # Verifica si el correo ya existe en la base de datos
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Obtiene el ID del contacto seleccionado si se está actualizando
        selected_item = tree.selection()
        if selected_item:
            current_id = tree.item(selected_item)['values'][0]
            # Verifica si existe el email excluyendo el contacto actual
            query = "SELECT COUNT(*) FROM contacts WHERE email = %s AND id != %s"
            cursor.execute(query, (email, current_id))
        else:
            # Para nuevos contactos, verifica si el email existe
            query = "SELECT COUNT(*) FROM contacts WHERE email = %s"
            cursor.execute(query, (email,))
            
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        
        # Si se encuentra el email, retorna mensaje de error
        if count > 0:
            return "Este correo electrónico ya está registrado en la base de datos."
    
    return ""

# Función para agregar un contacto
def add_contact():
    # Obtener los valores de los campos de entrada
    name = entry_name.get()
    phone = entry_phone.get()
    email = entry_email.get()

    # Validar cada campo usando las funciones de validación
    name_error = validate_name(name)
    phone_error = validate_phone(phone)
    email_error = validate_email(email)

    # Si hay algún error de validación, mostrar mensaje y salir
    if name_error or phone_error or email_error:
        messagebox.showerror("Error", "\n".join([name_error, phone_error, email_error]))
        return

    # Crear conexión a la base de datos
    connection = create_db_connection()
    if connection:
        # Crear cursor y ejecutar la inserción
        cursor = connection.cursor()
        query = "INSERT INTO contacts (name, phone, email) VALUES (%s, %s, %s)"
        values = (name, phone, email)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        
        # Mostrar mensaje de éxito
        messagebox.showinfo("Éxito", "Contacto agregado correctamente.")
        
        # Limpiar los campos de entrada
        entry_name.delete(0, tk.END)
        entry_phone.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        
        # Actualizar la tabla de contactos
        refresh_table()

# Función para actualizar un contacto
def update_contact():
    # Obtiene el elemento seleccionado del treeview
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Selecciona un contacto para actualizar.")
        return

    # Obtiene el ID del contacto y los valores de los campos
    contact_id = tree.item(selected_item)['values'][0]
    name = entry_name.get()
    phone = entry_phone.get()
    email = entry_email.get()

    # Valida los campos ingresados
    name_error = validate_name(name)
    phone_error = validate_phone(phone)
    email_error = validate_email(email)

    # Si hay errores de validación, muestra los mensajes y termina
    if name_error or phone_error or email_error:
        messagebox.showerror("Error", "\n".join([name_error, phone_error, email_error]))
        return

    # Establece conexión con la base de datos
    connection = create_db_connection()
    if connection:
        # Crea un cursor y ejecuta la actualización
        cursor = connection.cursor()
        query = "UPDATE contacts SET name=%s, phone=%s, email=%s WHERE id=%s"
        values = (name, phone, email, contact_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        
        # Muestra mensaje de éxito y actualiza la tabla
        messagebox.showinfo("Éxito", "Contacto actualizado correctamente.")
        refresh_table()

# Función para eliminar un contacto
def delete_contact():
    # Obtiene el elemento seleccionado del treeview
    selected_item = tree.selection()
    # Verifica si hay un elemento seleccionado, muestra advertencia si no
    if not selected_item:
        messagebox.showwarning("Advertencia", "Selecciona un contacto para eliminar.")
        return

    # Pide confirmación antes de eliminar
    confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este contacto?")
    if not confirm:
        return

    # Obtiene el ID del contacto del elemento seleccionado
    contact_id = tree.item(selected_item)['values'][0]
    # Crea la conexión a la base de datos
    connection = create_db_connection()
    if connection:
        # Crea el cursor y ejecuta la consulta de eliminación
        cursor = connection.cursor()
        query = "DELETE FROM contacts WHERE id=%s"
        values = (contact_id,)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        
        # Muestra mensaje de éxito
        messagebox.showinfo("Éxito", "Contacto eliminado correctamente.")
        # Actualiza la vista de la tabla
        refresh_table()
        # Limpia todos los campos de entrada
        entry_name.delete(0, tk.END)
        entry_phone.delete(0, tk.END)
        entry_email.delete(0, tk.END)

# Función para refrescar la tabla
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

# Función para buscar contactos en tiempo real
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

# Función para cargar los datos del contacto seleccionado en los campos
def load_contact_data(event):
    selected_item = tree.selection()
    if not selected_item:
        return

    contact_data = tree.item(selected_item)['values']
    entry_name.delete(0, tk.END)
    entry_name.insert(0, contact_data[1])
    entry_phone.delete(0, tk.END)
    entry_phone.insert(0, contact_data[2])
    entry_email.delete(0, tk.END)
    entry_email.insert(0, contact_data[3])

# Creación de la ventana principal
root = tk.Tk()
root.title("Agenda de Contactos")
root.geometry("900x800")
root.configure(bg="#F0F0F0")  # Fondo claro

# Estilo personalizado
style = ttk.Style()
style.theme_use("default")

# Colores y estilos
style.configure("TLabel", background="#F0F0F0", font=("Arial", 12))
style.configure("TButton", padding=8, font=("Arial", 12), background="#007ACC", foreground="white")
style.map("TButton", background=[("active", "#005EA3")])
style.configure("Treeview", font=("Arial", 12), background="#FFFFFF", foreground="#000000", rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#007ACC", foreground="white")

# Centrar los elementos en la ventana
frame = tk.Frame(root, bg="#F0F0F0")
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Campo de búsqueda
label_search = ttk.Label(frame, text="Buscar 🔎:")
label_search.grid(row=0, column=0, padx=5, pady=5)
entry_search = ttk.Entry(frame, width=30, font=("Arial", 12))
entry_search.grid(row=0, column=1, padx=5, pady=5, sticky="w")
entry_search.bind("<KeyRelease>", search_contacts)

# Campos de entrada
label_name = ttk.Label(frame, text="Nombre:")
label_name.grid(row=1, column=0, padx=5, pady=5)
entry_name = ttk.Entry(frame, width=30, font=("Arial", 12))
entry_name.grid(row=1, column=1, padx=5, pady=5, sticky="w")

label_phone = ttk.Label(frame, text="Teléfono 📞:",)
label_phone.grid(row=2, column=0, padx=5, pady=5)
entry_phone = ttk.Entry(frame, width=30, font=("Arial", 12))
entry_phone.grid(row=2, column=1, padx=5, pady=5, sticky="w")

label_email = ttk.Label(frame, text="Correo 📧:")
label_email.grid(row=3, column=0, padx=5, pady=5)
entry_email = ttk.Entry(frame, width=30, font=("Arial", 12))
entry_email.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Botones de acción
btn_add = ttk.Button(frame, text="Agregar Contacto", command=add_contact)
btn_add.grid(row=4, column=0, padx=5, pady=10)

btn_update = ttk.Button(frame, text="Actualizar Contacto", command=update_contact)
btn_update.grid(row=4, column=1, padx=5, pady=10)

btn_delete = ttk.Button(frame, text="Eliminar Contacto", command=delete_contact)
btn_delete.grid(row=4, column=2, padx=5, pady=10)

# Tabla de contactos
tree = ttk.Treeview(frame, columns=("ID", "Nombre", "Teléfono", "Correo"), show="headings", height=15)
tree.heading("ID", text="ID", anchor=tk.CENTER)
tree.heading("Nombre", text="Nombre", anchor=tk.CENTER)
tree.heading("Teléfono", text="Teléfono", anchor=tk.CENTER)
tree.heading("Correo", text="Correo", anchor=tk.CENTER)
tree.column("ID", width=50, anchor=tk.CENTER)
tree.column("Nombre", width=200, anchor=tk.CENTER)
tree.column("Teléfono", width=150, anchor=tk.CENTER)
tree.column("Correo", width=250, anchor=tk.CENTER)
tree.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

# Barra de desplazamiento
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
scrollbar.grid(row=5, column=4, sticky="ns")
tree.configure(yscrollcommand=scrollbar.set)

# Cargar los datos del contacto seleccionado
tree.bind("<<TreeviewSelect>>", load_contact_data)

# Cargar los contactos al iniciar la aplicación
refresh_table()

# Add these functions
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

# Botones de exportar e importar
btn_export = ttk.Button(frame, text="Exportar CSV", command=export_contacts)
btn_export.grid(row=4, column=3, padx=5, pady=10)

btn_import = ttk.Button(frame, text="Importar CSV", command=import_contacts)
btn_import.grid(row=4, column=4, padx=5, pady=10)


# Función que cambia de tema claro a oscuro y viceversa
def toggle_dark_mode():
    current_bg = root.cget("bg")
    if current_bg == "#F0F0F0":  # Modo claro
        #Colores modo claro
        root.configure(bg="#2B2B2B")
        frame.configure(bg="#2B2B2B")
        style.configure("TLabel", background="#2B2B2B", foreground="white")
        style.configure("TButton", background="#007ACC", foreground="white")
        style.configure("Treeview", background="#3C3F41", foreground="white", fieldbackground="#3C3F41")
        style.configure("Treeview.Heading", background="#007ACC", foreground="white")
        btn_theme.configure(text="☀️ Modo Claro")
    else:  # Modo oscuro
        # Colores modo oscuro
        root.configure(bg="#F0F0F0")
        frame.configure(bg="#F0F0F0")
        style.configure("TLabel", background="#F0F0F0", foreground="black")
        style.configure("TButton", background="#007ACC", foreground="white")
        style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
        style.configure("Treeview.Heading", background="#007ACC", foreground="white")
        btn_theme.configure(text="🌙 Modo Oscuro")

# Boton de cambio de modo claro/oscuro
btn_theme = ttk.Button(frame, text="🌙 Modo Oscuro", command=toggle_dark_mode)
btn_theme.grid(row=0, column=3, padx=5, pady=5)

root.mainloop()