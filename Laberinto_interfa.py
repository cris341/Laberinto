import time
import tkinter as tk
from tkinter import messagebox
from collections import deque
import heapq

# Logica 
laberinto = [
    [0, 0, 0, 0, 2, 0, 0, 1, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 1, 0, 3, 0],
    [1, 1, 0, 0, 3, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0],
    [0, 1, 2, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 3],
    [0, 1, 1, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0, 2, 9],
]
FILAS, COLUMNAS = len(laberinto), len(laberinto[0])
COINS_INICIALES = 30
INICIO = (0, 0)
META = next((i, j) for i in range(FILAS) for j in range(COLUMNAS) if laberinto[i][j] == 9)


def costo_celda(valor):
    return {0: 1, 2: 3, 3: 0.25, 9: 0}.get(valor, float("inf"))


def construir_grafo(lab):
    grafo = {}
    for i in range(len(lab)):
        for j in range(len(lab[0])):
            if lab[i][j] == 1:
                continue
            grafo[(i, j)] = [
                (i + di, j + dj)
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= i + di < len(lab) and 0 <= j + dj < len(lab[0]) and lab[i + di][j + dj] != 1
            ]
    return grafo


def reconstruir(predecesor, nodo):
    camino = []
    while nodo is not None:
        camino.append(nodo)
        nodo = predecesor[nodo]
    camino.reverse()
    return camino


def bfs_camino(grafo, inicio, objetivo):
    cola = deque([inicio])
    visitados = {inicio}
    predecesor = {inicio: None}
    while cola:
        nodo = cola.popleft()
        if nodo == objetivo:
            return reconstruir(predecesor, nodo), len(visitados)
        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                cola.append(vecino)
    return None, len(visitados)


def dfs_camino(grafo, inicio, objetivo):
    pila = [inicio]
    visitados = {inicio}
    predecesor = {inicio: None}
    while pila:
        nodo = pila.pop()
        if nodo == objetivo:
            return reconstruir(predecesor, nodo), len(visitados)
        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                pila.append(vecino)
    return None, len(visitados)

def ucs_camino(grafo, inicio, objetivo):
    dist = {inicio: 0}
    pred = {inicio: None}
    frontera = [(0, inicio)]
    while frontera:
        costo, nodo = heapq.heappop(frontera)
        if costo > dist[nodo]:
            continue
        if nodo == objetivo:
            camino = []
            while nodo is not None:
                camino.append(nodo)
                nodo = pred[nodo]
            camino.reverse()
            return camino, len(dist)          # camino, nodos descubiertos
        for v in grafo[nodo]:
            nuevo = costo + costo_celda(laberinto[v[0]][v[1]])
            if nuevo < dist.get(v, float("inf")):
                dist[v] = nuevo
                pred[v] = nodo
                heapq.heappush(frontera, (nuevo, v))
    return None, len(dist)
grafo = construir_grafo(laberinto)

# Para agregar BCU o A* después, basta con crear la función y añadirla aquí:
ALGORITMOS = {
    "BFS": (bfs_camino, "#C0392B"),   # rojo
    "DFS": (dfs_camino, "#2060C0"),   # azul
    "UCS": (ucs_camino, "#27AE60"),   # verde
}


#  INTERFAZ
CELDA = 56          # tamaño de cada celda en píxeles
OX, OY = 36, 56     # margen izquierdo (números de fila) y superior (título + columnas)
COLORES = {
    0: "#FFFFFF",   # libre
    1: "#2B2B2B",   # muro
    2: "#F4B6B6",   # penalización
    3: "#B6E3B6",   # premio
    9: "#FFD966",   # meta
}
COLOR_MANUAL = "#8E44AD"
DELAY_MS = 120      # velocidad de la animación


class Interfaz:
    def __init__(self, root):
        self.root = root
        root.title("Laberinto - Inteligencia Artificial")
        self.job = None          # id del after() de la animación
        self.modo = None         # None | "manual"
        self.pos = INICIO
        self.coins = COINS_INICIALES
        self.recorrido = []

        #Control de jugadores y resultados
        self.jug_actual = 1
        self.resultados = {}

        # diseño de la ventana
        ancho = OX + COLUMNAS * CELDA + 10
        alto = OY + FILAS * CELDA + 10
        self.canvas = tk.Canvas(root, width=ancho, height=alto, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        panel = tk.Frame(root)
        panel.grid(row=0, column=1, sticky="n", padx=(0, 12), pady=10)

        tk.Label(panel, text="Algoritmo", font=("Arial", 11, "bold")).pack(anchor="w")
        for nombre in ALGORITMOS:
            tk.Button(panel, text=f"Resolver con {nombre}", width=22,
                      command=lambda n=nombre: self.ejecutar(n)).pack(pady=2)

        tk.Label(panel, text="Juego", font=("Arial", 11, "bold")).pack(anchor="w", pady=(12, 0))
        tk.Button(panel, text="Jugar manualmente", width=22, command=self.iniciar_manual).pack(pady=2)
        tk.Button(panel, text="Limpiar tablero", width=22, command=self.reiniciar).pack(pady=2)

        tk.Label(panel, text="Información", font=("Arial", 11, "bold")).pack(anchor="w", pady=(12, 0))
        self.info = tk.Label(panel, text="Elige un algoritmo\no juega manualmente.",
                             justify="left", anchor="nw", width=35, height=13, font=("Arial", 10))
        self.info.pack(anchor="w")

        leyenda = tk.Frame(panel)
        leyenda.pack(anchor="w", pady=(8, 0))
        for cod, texto in [(0, "Libre · 1 coin"), (1, "Muro"), (2, "Penalización · 3"),
                           (3, "Premio · 0.25"), (9, "Meta · 0")]:
            fila = tk.Frame(leyenda)
            fila.pack(anchor="w")
            tk.Label(fila, bg=COLORES[cod], width=2, relief="solid", bd=1).pack(side="left", padx=(0, 6))
            tk.Label(fila, text=texto, font=("Arial", 9)).pack(side="left")

        # Teclas para el modo manual
        self.teclas = {"w": (-1, 0), "up": (-1, 0), "s": (1, 0), "down": (1, 0),
                       "a": (0, -1), "left": (0, -1), "d": (0, 1), "right": (0, 1)}
        root.bind("<Key>", self.on_key)

        self.dibujar_tablero()

    # dibujo 
    def centro(self, celda):
        i, j = celda
        return OX + j * CELDA + CELDA / 2, OY + i * CELDA + CELDA / 2

    def dibujar_tablero(self, titulo=""):
        c = self.canvas
        c.delete("all")
        c.create_text(OX + COLUMNAS * CELDA / 2, 16, text=titulo, font=("Arial", 12), tags="titulo")
        for j in range(COLUMNAS):
            c.create_text(OX + j * CELDA + CELDA / 2, OY - 12, text=str(j), font=("Arial", 9))
        for i in range(FILAS):
            c.create_text(OX - 14, OY + i * CELDA + CELDA / 2, text=str(i), font=("Arial", 9))
            for j in range(COLUMNAS):
                x0, y0 = OX + j * CELDA, OY + i * CELDA
                c.create_rectangle(x0, y0, x0 + CELDA, y0 + CELDA,
                                   fill=COLORES[laberinto[i][j]], outline="#CCCCCC")

    def dibujar_paso(self, camino, i, color):
        """Dibuja la línea hacia camino[i] y un círculo numerado con el paso i."""
        c = self.canvas
        x, y = self.centro(camino[i])
        if i > 0:
            xa, ya = self.centro(camino[i - 1])
            c.create_line(xa, ya, x, y, fill=color, width=4, tags="camino")
        r = CELDA * 0.3
        c.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="white", width=2, tags=("camino", "nodo"))
        c.create_text(x, y, text=str(i), fill="white", font=("Arial", 11, "bold"), tags=("camino", "nodo"))
        c.tag_raise("nodo")  # círculos siempre encima de las líneas

    def set_titulo(self, texto):
        self.canvas.itemconfigure("titulo", text=texto)

    def set_info(self, texto):
        self.info.config(text=texto)

    # control 
    def cancelar_animacion(self):
        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

    def reiniciar(self):
        self.cancelar_animacion()
        self.modo = None
        self.dibujar_tablero()
        self.set_info("Elige un algoritmo\no juega manualmente.")

    # modo automático 
    def ejecutar(self, nombre):
        self.reiniciar()
        funcion, color = ALGORITMOS[nombre]

        t0 = time.perf_counter()
        camino, nodos = funcion(grafo, INICIO, META)
        tiempo = time.perf_counter() - t0

        if camino is None:
            self.set_info(f"{nombre} no encontró\nun camino a la meta.")
            return

        gasto = sum(costo_celda(laberinto[x][y]) for x, y in camino[1:])
        restantes = COINS_INICIALES - gasto
        pasos = len(camino) - 1
        self.set_titulo(f"{nombre}: {pasos} movimientos, {restantes:g} coins finales")

        texto = (f"Algoritmo: {nombre}\n"
                 f"Movimientos: {pasos}\n"
                 f"Coins gastadas: {gasto:g}\n"
                 f"Coins restantes: {restantes:g}\n"
                 f"Nodos visitados: {nodos}\n"
                 f"Tiempo: {tiempo * 1e6:.1f} µs")
        if restantes < 0:
            texto += "\n⚠ Las coins no alcanzan\npara este camino."
        self.set_info(texto)
        self.animar(camino, color, 0)

    def animar(self, camino, color, i):
        if i >= len(camino):
            self.job = None
            return
        self.dibujar_paso(camino, i, color)
        self.job = self.root.after(DELAY_MS, self.animar, camino, color, i + 1)

    # modo manual 
    def iniciar_manual(self):
        self.reiniciar()
        self.modo = "manual"
        self.resultados = {}
        self.jug_actual = 1
        self.inicia_jugador()

    def inicia_jugador(self):
        self.modo = "manual"
        self.pos = INICIO # reinicia el juego para un nuevo jugador
        self.coins = COINS_INICIALES
        self.recorrido = [INICIO]

        nombre = f"Jugador {self.jug_actual}"
        self.dibujar_tablero(f"Modo manual - {nombre}: {self.coins:g} coins")
        color = COLOR_MANUAL if self.jug_actual % 2 == 1 else "#E622CC"  # alterna colores
        self.dibujar_paso(self.recorrido, 0, color)
        
        self.actualizar_manual(f"{nombre}, BIENVENIDO AL JUEGO.\n"
                               f"Gana quien complete el laberinto con más coins.\n")

    def actualizar_manual(self, mensaje):
        self.set_titulo(f"jugador {self.jug_actual}: "f"Manual: {len(self.recorrido) - 1} movimientos, {self.coins:g} coins")
        self.set_info(f"Jugador {self.jug_actual}\n" f"Coins: {self.coins:g}\nMovimientos: {len(self.recorrido) - 1}\n\n{mensaje}")

    def on_key(self, event):
        if self.modo != "manual":
            return
        # Detecta la tecla presionada y calcula el nuevo movimiento
        movimiento = self.teclas.get(event.keysym.lower())
        if movimiento is None:
            return
        #Calcula la nueva posición
        nueva = (self.pos[0] + movimiento[0], self.pos[1] + movimiento[1])

        # Verifica si el movimiento es válido (dentro del laberinto y no hacia un muro)
        if nueva not in grafo[self.pos]:
            self.actualizar_manual("Movimiento inválido\n(muro o borde).")
            return

        costo = costo_celda(laberinto[nueva[0]][nueva[1]])
        if self.coins < costo:
            self.finalizar_turno_manual(False, "No tienes suficientes coins para entrar a esa celda.")      
            return

        self.coins -= costo
        self.pos = nueva
        self.recorrido.append(nueva)
        color = COLOR_MANUAL if self.jug_actual % 2 == 1 else "#E622CC"
        self.dibujar_paso(self.recorrido, len(self.recorrido) - 1, color)

        celda = laberinto[nueva[0]][nueva[1]]
        if celda == 9:
            self. actualizar_manual("🏁 ¡Llegaste a la meta!")
            self.finalizar_turno_manual(True, "¡Felicidades! Llegaste a la meta.")
        elif self.coins <= 0:
            self.actualizar_manual("⚠ Te quedaste sin coins.")
            self.finalizar_turno_manual(False, "Te quedaste sin coins.")
        elif celda == 2:
            self.actualizar_manual("⚠ ¡Penalización! (-3)")
        elif celda == 3:
            self.actualizar_manual("🎁 ¡Premio! (-0.25)")
        else:
            self.actualizar_manual("Movimiento realizado.")

    def finalizar_turno_manual(self, gano, mensaje):
        self.modo = None
        numero = self.jug_actual
        gastadas = COINS_INICIALES - self.coins

        self.resultados[numero] = {
            "gano": gano,
            "coins": self.coins,
            "gastadas": gastadas,
            "movimientos": len(self.recorrido) - 1,
        }

        resultado = self.resultados[numero]
        resumen = (
            f"JUGADOR {numero}\n\n"
            f"Resultado: {'Llegó a la meta' if gano else 'Perdió'}\n"
            f"Detalle: {mensaje}\n"
            f"Movimientos: {resultado['movimientos']}\n"
            f"Monedas gastadas: {resultado['gastadas']:g}\n"
            f"Monedas restantes: {resultado['coins']:g}"
        )
        messagebox.showinfo(f"Resultados del Jugador {numero}", resumen, parent=self.root)

        if numero == 1:
            # El jugador 1 terminó. Se reinicia todo para el jugador 2.
            messagebox.showinfo(
                "Turno del Jugador 2",
                "El tablero se reinició.\n"
                "El Jugador 2 comienza con 30 monedas.\n"
                "¡Buena suerte!",
                parent=self.root
            )
            self.jug_actual = 2
            self.inicia_jugador()
            return

        # El jugador 2 terminó: comparar los dos resultados.
        self.modo = None
        j1 = self.resultados[1]
        j2 = self.resultados[2]

        if j1["gano"] and j2["gano"]:
            if j1["coins"] > j2["coins"]:
                ganador = "¡GANA EL JUGADOR 1!"
            elif j2["coins"] > j1["coins"]:
                ganador = "¡GANA EL JUGADOR 2!"
            else:
                ganador = "¡EMPATE! Ambos llegaron con las mismas monedas."
        elif j1["gano"]:
            ganador = "¡GANA EL JUGADOR 1! Solo él llegó a la meta."
        elif j2["gano"]:
            ganador = "¡GANA EL JUGADOR 2! Solo él llegó a la meta."
        else:
            ganador = "NINGÚN JUGADOR LLEGÓ A LA META. No hay ganador."

        comparacion = (
            "RESULTADO FINAL\n\n"
            f"Jugador 1: {'Llegó a la meta' if j1['gano'] else 'No llegó a la meta'}\n"
            f"Monedas gastadas: {j1['gastadas']:g}\n"
            f"Monedas restantes: {j1['coins']:g}\n"
            f"Movimientos: {j1['movimientos']}\n\n"
            f"Jugador 2: {'Llegó a la meta' if j2['gano'] else 'No llegó a la meta'}\n"
            f"Monedas gastadas: {j2['gastadas']:g}\n"
            f"Monedas restantes: {j2['coins']:g}\n"
            f"Movimientos: {j2['movimientos']}\n\n"
            f"{ganador}"
        )

        self.dibujar_tablero("Partida finalizada")
        self.set_info(comparacion)
        messagebox.showinfo("Ganador del laberinto", comparacion, parent=self.root)

root = tk.Tk()
Interfaz(root)
root.mainloop()