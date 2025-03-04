# Importaciones necesarias para el funcionamiento del juego
import tkinter as tk
from tkinter import messagebox, ttk  # Para ventanas emergentes y widgets mejorados
import random  # Para generar posiciones aleatorias de minas
import time  # Para medir el tiempo transcurrido durante el juego
import json  # Para guardar y cargar récords
import pygame 

# Configuración inicial del juego
DIFICULTADES = {
    "Facil": {"filas": 6, "columnas": 6, "minas": 6},
    "Medio": {"filas": 12, "columnas": 12, "minas": 15},
    "Dificil": {"filas": 16, "columnas": 16, "minas": 50}
}

# Paleta de colores para el fondo de los números
COLORES_FONDO = {
    1: "#e7f3fe",  # Azul claro
    2: "#c8e6c9",  # Verde claro
    3: "#ffcdd2",  # Rojo claro
    4: "#e1bee7",  # Púrpura claro
    5: "#ffe0b2",  # Naranja claro
    6: "#b2ebf2",  # Cian claro
    7: "#d7ccc8",  # Gris claro
    8: "#f5f5f5"   # Blanco grisáceo
}

# Archivo para guardar los récords
RECORDS_FILE = "records.json"

class Buscaminas:
    def __init__(self, root):
        self.root = root
        self.root.title("Buscaminas")  # Título de la ventana principal
        self.dificultad_seleccionada = None  # Dificultad seleccionada por el usuario
        self.tablero = None  # Representación interna del tablero
        self.botones = []  # Lista de botones que representan el tablero visual
        self.inicio_tiempo = None  # Marca el inicio del temporizador
        self.tiempo_label = None  # Etiqueta que muestra el tiempo transcurrido
        self.banderas_usadas = 0  # Número de banderas colocadas
        self.banderas_totales = 0  # Número total de banderas disponibles
        self.banderas_label = None  # Etiqueta que muestra el estado de las banderas
        self.records = self.cargar_records()  # Carga los récords desde el archivo
        self.crear_menu_dificultad()  # Muestra el menú de selección de dificultad
        self.sonido_mina = ""
        self.sonido_bandera = ""
        # Inicializar pygame para manejar el sonido
        pygame.mixer.init()

        # Cargar el archivo de sonido para cuando se pulse una mina
        try:
            self.sonido_mina = pygame.mixer.Sound("sonidos/peo.mp3")
            self.sonido_bandera = pygame.mixer.Sound("sonidos/chiclin.mp3")
        except FileNotFoundError:
            print("Error: No se encontró el archivo de sonido 'peo.mp3'.")
            self.sonido_mina = None

    # Carga los récords desde el archivo JSON
    def cargar_records(self):
        """Carga los récords desde el archivo JSON."""
        try:
            with open(RECORDS_FILE, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"Fácil": None, "Medio": None, "Difícil": None}

    def guardar_records(self):
        """Guarda los récords en el archivo JSON."""
        with open(RECORDS_FILE, "w") as file:
            json.dump(self.records, file)
    
    # Guarda los récords en el archivo JSON
    def guardar_record(self, tiempo):
        """Guarda el récord si es el mejor tiempo para la dificultad actual."""
        dificultad = self.combobox_dificultad.get()
        if self.records[dificultad] is None or tiempo < self.records[dificultad]:
            self.records[dificultad] = tiempo
            self.guardar_records()  # Llama al método correcto
            messagebox.showinfo("Récord", f"¡Nuevo récord para {dificultad}: {tiempo} segundos!")

    # Muestra una ventana con los récords actuales
    def mostrar_ventana_records(self):
        """Muestra una ventana con la tabla de récords."""
        # Crear una nueva ventana
        ventana_records = tk.Toplevel(self.root)
        ventana_records.title("Tabla de Récords")
        ventana_records.geometry("400x300")
        ventana_records.resizable(False, False)

        # Frame principal
        frame = tk.Frame(ventana_records, bg="#f0f0f0")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Título de la ventana
        titulo = tk.Label(frame, text="Tabla de Récords", font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#333333")
        titulo.grid(row=0, column=0, columnspan=2, pady=10)  # Usar grid para el título

        # Mostrar los récords en una tabla
        for i, dificultad in enumerate(DIFICULTADES.keys()):
            tiempo = self.records[dificultad]
            tiempo_texto = f"{tiempo} segundos" if tiempo is not None else "Sin récord"

            # Etiqueta para la dificultad
            etiqueta_dificultad = tk.Label(frame, text=f"{dificultad}:", font=("Arial", 14), bg="#f0f0f0", fg="#333333")
            etiqueta_dificultad.grid(row=i + 1, column=0, sticky="w", pady=5)  # Usar grid para las etiquetas

            # Etiqueta para el tiempo
            etiqueta_tiempo = tk.Label(frame, text=tiempo_texto, font=("Arial", 14), bg="#f0f0f0", fg="#333333")
            etiqueta_tiempo.grid(row=i + 1, column=1, sticky="w", pady=5)  # Usar grid para las etiquetas

        # Botón para cerrar la ventana
        boton_cerrar = tk.Button(frame, text="Cerrar", font=("Arial", 14), bg="#f44336", fg="white", command=ventana_records.destroy)
        boton_cerrar.grid(row=len(DIFICULTADES) + 1, column=0, columnspan=2, pady=20)  # Usar grid para el botón


    # Crea el menú inicial donde el usuario selecciona la dificultad
    def crear_menu_dificultad(self):
        """Crea el menú de inicio con un título, un Combobox y botones estilizados."""
        # Limpiar la ventana actual
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame principal
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.root.geometry("400x400")  # Tamaño del menú inicial

        # Título del menú
        titulo = tk.Label(frame, text="Bienvenido al Buscaminas\nmasón de Héctor", font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#333333")
        titulo.pack(pady=20)

        # Etiqueta para el Combobox
        label = tk.Label(frame, text="Selecciona la dificultad:", font=("Arial", 14), bg="#f0f0f0", fg="#333333")
        label.pack(pady=10)

        # Combobox para seleccionar la dificultad
        self.combobox_dificultad = ttk.Combobox(frame, values=list(DIFICULTADES.keys()), state="readonly", font=("Arial", 12))
        self.combobox_dificultad.set("Facil")  # Valor predeterminado
        self.combobox_dificultad.pack(pady=10)

        # Botón para jugar
        boton_jugar = tk.Button(frame, text="Jugar", font=("Arial", 14), bg="#4CAF50", fg="white", command=self.iniciar_juego)
        boton_jugar.pack(pady=10)

        # Botón para ver los récords
        boton_records = tk.Button(frame, text="Récords", font=("Arial", 14), bg="#2196F3", fg="white", command=self.mostrar_ventana_records)
        boton_records.pack(pady=10)

        # Botón para salir
        boton_salir = tk.Button(frame, text="Salir", font=("Arial", 14), bg="#f44336", fg="white", command=self.root.quit)
        boton_salir.pack(pady=10)

    # Inicia el juego con la dificultad seleccionada
    def iniciar_juego(self):
        """Inicia el juego con la dificultad seleccionada."""
        dificultad = self.combobox_dificultad.get()
        if not dificultad:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una dificultad.")
            return

        # Almacenar la dificultad seleccionada
        self.dificultad_seleccionada = dificultad

        # Obtener configuración de la dificultad
        config = DIFICULTADES[dificultad]
        self.filas, self.columnas, self.minas = config["filas"], config["columnas"], config["minas"]
        self.banderas_totales = self.minas
        self.banderas_usadas = 0

        # Limpiar la ventana actual
        for widget in self.root.winfo_children():
            widget.destroy()

        # Ajustar el tamaño de la ventana según la dificultad
        self.root.geometry(f"{self.columnas * 35}x{self.filas * 35 + 150}")

        # Inicializar variables del juego
        self.generar_tablero()
        self.colocar_minas()
        self.calcular_adyacencias()

        # Crear el tablero gráfico
        self.crear_tablero()

        # Contador de tiempo
        self.inicio_tiempo = time.time()
        self.actualizar_tiempo()
        
        # Para detectar doble clic derecho
        self.ultimo_clic_derecho = None  

    # Genera una matriz vacía para representar el tablero
    def generar_tablero(self):
        """Genera una matriz para representar el tablero."""
        self.tablero = [[{"mina": False, "adyacentes": 0, "revelado": False, "bandera": False} for _ in range(self.columnas)] for _ in range(self.filas)]

    # Coloca las minas aleatoriamente en el tablero
    def colocar_minas(self):
        """Coloca las minas aleatoriamente en el tablero."""
        minas_colocadas = 0
        while minas_colocadas < self.minas:
            fila = random.randint(0, self.filas - 1)
            columna = random.randint(0, self.columnas - 1)
            if not self.tablero[fila][columna]["mina"]:
                self.tablero[fila][columna]["mina"] = True
                minas_colocadas += 1

    # Calcula el número de minas adyacentes para cada celda
    def calcular_adyacencias(self):
        """Calcula el número de minas adyacentes para cada celda."""
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if not self.tablero[fila][columna]["mina"]:
                    self.tablero[fila][columna]["adyacentes"] = self.contar_minas_adyacentes(fila, columna)

    # Cuenta las minas adyacentes a una celda específica
    def contar_minas_adyacentes(self, fila, columna):
        """Cuenta las minas adyacentes a una celda específica."""
        minas = 0
        for df in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if df == 0 and dc == 0:
                    continue
                f, c = fila + df, columna + dc
                if 0 <= f < self.filas and 0 <= c < self.columnas and self.tablero[f][c]["mina"]:
                    minas += 1
        return minas

    # Crea la interfaz gráfica del tablero
    def crear_tablero(self):
        """Crea la interfaz gráfica del tablero."""
        frame = tk.Frame(self.root, bg="#2c3e50")
        frame.pack(pady=10)

        self.botones = []
        for fila in range(self.filas):
            fila_botones = []
            for columna in range(self.columnas):
                boton = tk.Button(frame, width=2, height=1,
                                bg="#e0e0e0", relief="raised", bd=2, font=("Arial", 10, "bold"))
                boton.grid(row=fila, column=columna)
                boton.bind("<Button-1>", lambda event, f=fila, c=columna: self.revelar_celda(f, c))  # Clic izquierdo
                boton.bind("<Button-3>", lambda event, f=fila, c=columna: self.manejar_clic_derecho(f, c))  # Clic derecho
                fila_botones.append(boton)
            self.botones.append(fila_botones)

        # Etiqueta de tiempo
        self.tiempo_label = tk.Label(self.root, text="Tiempo: 0 segundos", font=("Arial", 12), bg="#2c3e50", fg="#ecf0f1")
        self.tiempo_label.pack(pady=10)

        # Etiqueta de banderas
        self.banderas_label = tk.Label(self.root, text=f"Banderas: {self.banderas_usadas}/{self.banderas_totales}", font=("Arial", 12), bg="#2c3e50", fg="#ecf0f1")
        self.banderas_label.pack(pady=10)

    # Actualiza el contador de tiempo cada segundo
    def actualizar_tiempo(self):
        """Actualiza el contador de tiempo."""
        if self.inicio_tiempo:
            tiempo_transcurrido = int(time.time() - self.inicio_tiempo)
            self.tiempo_label.config(text=f"Tiempo: {tiempo_transcurrido} segundos")
            self.root.after(1000, self.actualizar_tiempo)
            
    # Revela el contenido de una celda
    def revelar_celda(self, fila, columna):
        """Revela el contenido de una celda."""
        celda = self.tablero[fila][columna]

        if celda["bandera"] or celda["revelado"]:
            return

        celda["revelado"] = True
        boton = self.botones[fila][columna]

        if celda["mina"]:
            boton.config(text="💣", bg="#e74c3c", relief="sunken", state="disabled")
            # Reproducir el sonido del peo si está disponible
            if self.sonido_mina:
                self.sonido_mina.play()
            self.destapar_tablero_perdido()  # Destapar el tablero antes de mostrar el mensaje
            self.mostrar_mensaje_final("¡Has perdido!")
        else:
            color_texto = COLORES_FONDO.get(celda["adyacentes"], "black")  # Color del texto
            color_fondo = COLORES_FONDO.get(celda["adyacentes"], "#b0b0b0")  # Color del fondo
            texto = str(celda["adyacentes"]) if celda["adyacentes"] > 0 else ""
            boton.config(text=texto, bg=color_fondo, fg=color_texto, relief="sunken", state="disabled")
            if celda["adyacentes"] == 0:
                self.revelar_celdas_adyacentes(fila, columna)

        if self.verificar_victoria():
            tiempo = int(time.time() - self.inicio_tiempo)
            self.guardar_record(tiempo)
            self.mostrar_mensaje_final("¡Has ganado!")

    # Revela recursivamente las celdas adyacentes sin minas
    def revelar_celdas_adyacentes(self, fila, columna):
        """Revela recursivamente las celdas adyacentes si no hay minas cercanas."""
        for df in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if df == 0 and dc == 0:
                    continue
                f, c = fila + df, columna + dc
                if 0 <= f < self.filas and 0 <= c < self.columnas:
                    self.revelar_celda(f, c)
                    
    # Verifica si el jugador ha ganado
    def verificar_victoria(self):
        """Verifica si el jugador ha ganado."""
        for fila in range(self.filas):
            for columna in range(self.columnas):
                celda = self.tablero[fila][columna]
                if not celda["mina"] and not celda["revelado"]:
                    return False
        return True

    # Coloca o quita una bandera en una celda
    def colocar_bandera(self, fila, columna):
        """Coloca o quita una bandera en una celda."""
        celda = self.tablero[fila][columna]
        boton = self.botones[fila][columna]

        if celda["revelado"]:
            return

        if celda["bandera"]:
            # Quitar bandera
            celda["bandera"] = False
            boton.config(text="", bg="#e0e0e0", relief="raised", state="normal")
            self.banderas_usadas -= 1
        else:
            if self.banderas_usadas < self.banderas_totales:
                # Colocar bandera
                 # Reproducir el sonido del peo si está disponible
                if self.sonido_bandera:
                    self.sonido_bandera.play()
                celda["bandera"] = True
                boton.config(text="🚩", bg="#f1c40f", relief="raised", state="normal")
                self.banderas_usadas += 1

        # Actualizar etiqueta de banderas
        self.banderas_label.config(text=f"Banderas: {self.banderas_usadas}/{self.banderas_totales}")

    # Muestra un mensaje al final del juego
    def mostrar_mensaje_final(self, mensaje):
        """Muestra un mensaje al final del juego."""
        self.inicio_tiempo = None  # Detener el contador de tiempo
        messagebox.showinfo("Fin del juego", mensaje)
        self.volver_al_menu()

    # Destapa todo el tablero cuando el jugador pierde
    def destapar_tablero_perdido(self):
        """Destapa todo el tablero cuando el jugador pierde."""
        for fila in range(self.filas):
            for columna in range(self.columnas):
                celda = self.tablero[fila][columna]
                boton = self.botones[fila][columna]

                if celda["mina"]:
                    boton.config(text="💣", bg="#e74c3c", relief="sunken", state="disabled")
                elif celda["adyacentes"] > 0:
                    color_texto = COLORES_FONDO.get(celda["adyacentes"], "black")
                    color_fondo = COLORES_FONDO.get(celda["adyacentes"], "#b0b0b0")
                    texto = str(celda["adyacentes"])
                    boton.config(text=texto, bg=color_fondo, fg=color_texto, relief="sunken", state="disabled")
                else:
                    boton.config(bg="#b0b0b0", relief="sunken", state="disabled")

    def guardar_record(self, tiempo):
        """Guarda el récord si es el mejor tiempo para la dificultad actual."""
        # Usar la dificultad almacenada en la variable de instancia
        dificultad = self.dificultad_seleccionada

        if self.records[dificultad] is None or tiempo < self.records[dificultad]:
            self.records[dificultad] = tiempo
            self.guardar_records()
            messagebox.showinfo("Récord", f"¡Nuevo récord para {dificultad}: {tiempo} segundos!")

    def volver_al_menu(self):
        """Vuelve al menú principal."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.crear_menu_dificultad()
        
    def colocar_interrogacion(self, fila, columna):
        """Coloca o quita una interrogación en una celda."""
        celda = self.tablero[fila][columna]
        boton = self.botones[fila][columna]

        if celda["revelado"]:
            return

        if not celda.get("interrogacion", False):
            # Colocar interrogación
            celda["interrogacion"] = True
            boton.config(text="❔", bg="#d3d3d3", relief="raised", state="normal")
        else:
            # Limpiar la celda
            celda["interrogacion"] = False
            boton.config(text="", bg="#e0e0e0", relief="raised", state="normal")

    def manejar_clic_derecho(self, fila, columna):
        """Maneja el clic derecho para colocar/quitar banderas o interrogaciones."""
        tiempo_actual = time.time()

        if self.ultimo_clic_derecho is not None and tiempo_actual - self.ultimo_clic_derecho < 0.3:
            # Doble clic derecho detectado
            self.colocar_interrogacion(fila, columna)
            self.ultimo_clic_derecho = None  # Reiniciar el temporizador
        else:
            # Solo un clic derecho
            self.colocar_bandera(fila, columna)
            self.ultimo_clic_derecho = tiempo_actual  # Registrar el tiempo del clic
            
# Iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = Buscaminas(root)
    root.mainloop()