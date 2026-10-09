import time 

laberinto = [
    [0, 0, 0, 0, 2, 0, 0, 1, 0],  # fila 0
    [0, 1, 1, 1, 0, 1, 0, 1, 0],  # fila 1
    [0, 0, 0, 1, 0, 1, 0, 3, 0],  # fila 2
    [1, 1, 0, 0, 3, 1, 1, 1, 0],  # fila 3
    [0, 0, 0, 1, 0, 0, 0, 1, 0],  # fila 4
    [0, 1, 2, 1, 0, 1, 0, 1, 0],  # fila 5
    [0, 1, 0, 0, 0, 1, 0, 0, 3],  # fila 6 
    [0, 1, 1, 1, 0, 0, 0, 1, 0],  # fila 7
    [1, 0, 0, 0, 0, 1, 0, 2, 9]   # fila 8 
]

FILAS = len(laberinto)
COLUMNAS = len(laberinto[0])

# Jugador inicial
pos = [0, 0]
coins = 30  # cantidad inicial de monedas

# Función de costo
def costo_celda(valor):
    if valor == 0:  # libre
        return 1
    elif valor == 2:  # penalización
        return 3
    elif valor == 3:  # premio
        return 0.25
    elif valor == 9:  # meta
        return 0
    else:  # muro
        return float("inf")

#Immplementacion de grafos de estado 
def impl_grafo(lab):
    grafo = {} #Diccionario de grafos 
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if lab[i][j] == 1:
                continue
            estado = (i,j)
            grafo[estado]=[]
            movimientos = [(-1,0),(1,0),(0,-1),(0,1)]
            #conteo de movimientos 
            for dx, dy in movimientos:
                nx = i + dx
                ny = j + dy 
                if 0 <=nx < FILAS and 0<= ny < COLUMNAS:
                    if lab[nx][ny] != 1:
                        grafo[estado].append((nx,ny))

    return grafo 

grafo = impl_grafo(laberinto)

#Implementacion del algoritmo BFS (PENDIENTE)
def bfs_camino(grafo, inicio, objetivo):
    cola = [inicio]
    visitados = {inicio}
    predecesor = {inicio: None}
    while cola:
        nodo = cola.pop(0)
        if nodo == objetivo:
            # reconstrucción del camino
            camino = []
            while nodo is not None:
                camino.append(nodo)
                nodo = predecesor[nodo]
            return list(reversed(camino)), len(visitados)  #Devolver camino y cantidad de nodos visitados
        
        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                cola.append(vecino) 
    return None, len(visitados)  

#Implementacion del algoritmo DFS 
def dfs_camino(grafo,inicio,objetivo):
    pila=[inicio]
    visitados = {inicio} #guardar estados visitados
    predecesor = {inicio: None} #de donde viene los estados 
    while pila:
        nodo = pila.pop()

        #verifica
        if nodo == objetivo: 
            # reconstrucción del camino
            camino = []
            while nodo is not None:
                camino.append(nodo)
                nodo = predecesor[nodo]

            camino.reverse()
            return camino, len(visitados)  #Devolver camino y cantidad de nodos visitados

        #verificar los nodos vecinos del actual 
        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                pila.append(vecino) 

    # si no se encuentra el objetivo, devolver None y la cantidad de nodos visitados           
    return None, len(visitados)


# Imprimir tablero
def imprimir_tablero(lab, pos, coins):
    print(f"\nMonedas actuales: {coins}")
    for i in range(len(lab)):
        fila = []
        for j in range(len(lab[0])):
            if (i, j) == tuple(pos):
                fila.append(8)
            else:
                fila.append(lab[i][j])
        print(fila)
    print()

def imprimir_camino(lab, camino):
    en_camino = set(camino)
    print("\nRecorrido (* = camino):")
    for i in range(len(lab)):
        fila = []
        for j in range(len(lab[0])):
            if (i, j) in en_camino:
                fila.append("*")
            else:
                fila.append(str(lab[i][j]))
        print(" ".join(fila))
    print()

# --- Juego manual entre jugadores ---
def jugar(nombre):

    pos = [0, 0]
    coins = 30

    print("\n" + "=" * 40)
    print(f"🎮 Turno de {nombre}")
    print("=" * 40)

    print("🐭 Bienvenido al laberinto de 9x9 🎮")
    print("Reglas:")
    print("- w = arriba, s = abajo, a = izquierda, d = derecha")
    print("- Celdas normales cuestan 1 coin")
    print("- Celda penalización (2) cuesta 3 coins")
    print("- Celda premio (3) cuesta 0.25 coins")
    print("- Si llegas a 0 coins pierdes ❌")
    print("- Llega a la meta para ganar 🎉")

    imprimir_tablero(laberinto, pos, coins)

    while True:

        mov = input(f"{nombre}, ingresa tu movimiento (w/a/s/d): ").strip().lower()

        if mov not in ["w", "a", "s", "d"]:
            print("Movimiento inválido ❌")
            continue

        nueva_pos = pos.copy()

        if mov == "w":
            nueva_pos[0] -= 1
        elif mov == "s":
            nueva_pos[0] += 1
        elif mov == "a":
            nueva_pos[1] -= 1
        elif mov == "d":
            nueva_pos[1] += 1

        x, y = nueva_pos

        # Verificar límites
        if not (0 <= x < FILAS and 0 <= y < COLUMNAS):
            print("No puedes salirte del tablero 🚧")
            continue

        # Verificar conexión en el grafo
        estado_actual = tuple(pos)
        nuevo_estado = (x, y)

        if nuevo_estado not in grafo[estado_actual]:
            print("Movimiento inválido: hay un muro 🚧")
            continue

        # Calcular costo
        costo = costo_celda(laberinto[x][y])

        # Verificar si tiene suficientes coins
        if coins < costo:
            print("❌ No tienes suficientes coins para entrar a esta celda.")
            print("❌ Te quedaste sin coins. ¡Perdiste!")
            
            return {
                "nombre": nombre,
                "gano": False,
                "coins": 0
            }

        # Restar costo
        coins -= costo
        pos = nueva_pos

        # Mensajes de penalización y premio
        if laberinto[x][y] == 2:
            print("⚠️ ¡PENALIZACIÓN! Esta celda cuesta 3 coins.")

        elif laberinto[x][y] == 3:
            print("🎁 ¡PREMIO! Esta celda cuesta solo 0.25 coins.")

        imprimir_tablero(laberinto, pos, coins)

        # Verificar si se quedó sin coins
        if coins <= 0 and laberinto[x][y] != 9:
            print("❌ Te quedaste sin coins. ¡Perdiste!")

            return {
                "nombre": nombre,
                "gano": False,
                "coins": 0
            }

        # Verificar meta
        if laberinto[x][y] == 9:
            print(f"🎉 ¡{nombre} ha llegado a la meta!")
            print(f"✅ Coins restantes: {coins}")

            return {
                "nombre": nombre,
                "gano": True,
                "coins": coins
            }

#Modo automático (BFS)
def jugar_bfs_aut(grafo):
    inicio = (0, 0)
    objetivo = (8, 8)

    print("\n" + "=" * 50)
    print("MODO AUTOMÁTICO - BFS")
    print("=" * 50)

    # Medir tiempo de ejecución
    tiempo_inicial = time.perf_counter()
    camino, nodos_visitados = bfs_camino(grafo, inicio, objetivo)
    tiempo_final = time.perf_counter()
    tiempo_ejecucion = tiempo_final - tiempo_inicial

    if camino is None:
        print("❌ El algoritmo BFS no encontró un camino hacia la meta.")
        return None

    # Resultados
    print(f" Camino encontrado por BFS: {camino}")
    print(f" Longitud del camino: {len(camino) - 1} pasos")
    print(f" Nodos visitados: {nodos_visitados}")
    print(f" Tiempo de ejecución: {tiempo_ejecucion:.6f} segundos")

    # Mostrar el recorrido sobre el tablero
    imprimir_camino(laberinto, camino)

    return {"camino": camino, "nodos": nodos_visitados, "tiempo": tiempo_ejecucion}
#Modo automático (DFS)
def jugar_dfs_aut(grafo):

    inicio = (0, 0)
    objetivo = (8, 8)

    print("\n" + "=" * 50)
    print("MODO AUTOMÁTICO - DFS")
    print("=" * 50)

    #Medir tiempo de ejecución
    tiempo_inicial = time.perf_counter()
    camino, nodos_visitados = dfs_camino (grafo, inicio, objetivo)

    tiempo_final = time.perf_counter()
    tiempo_ejecucion = tiempo_final - tiempo_inicial

    #Verificar
    if camino is None:
        print("❌ el algoritmo DFS no encontró un camino hacia la meta :c.")
        return
    #Resultados
    print(f" Camino encontrado por DFS: {camino}")
    print(f" Nodos visitados: {nodos_visitados}")
    print(f" Tiempo de ejecución: {tiempo_ejecucion:.6f} segundos")

    coins = 30
    print(f"\nMonedas iniciales: {coins}")
    imprimir_camino(laberinto, camino)

    #recorrer el camino y calcular coins
    for posicion in camino[1:]:
        x,y = posicion
        costo = costo_celda(laberinto[x][y])

        if coins < costo:
            print("❌ No tienes suficientes coins para entrar a esta celda.")
            print("❌ Te quedaste sin coins. ¡Perdiste!")
            return {"gano": False,"coins": 0}

        coins -= costo
        print(f"Moviendo a {posicion}, costo: {costo}, coins restantes: {coins}")

        #penalización y premio
        if laberinto[x][y] == 2:
            print("⚠️ ¡PENALIZACIÓN! Esta celda cuesta 3 coins.")

        elif laberinto[x][y] == 3:
            print("🎁 ¡PREMIO! Esta celda cuesta solo 0.25 coins.")

        #perdida 
        if coins <= 0 and laberinto[x][y] != 9:
            print("❌ Te quedaste sin coins. ¡Perdiste!")
            return {"gano": False,"coins": 0}
        #meta
        if laberinto[x][y] == 9:
            print(f"🎉 ¡El jugador ha llegado a la meta!")
            print(f"✅ Coins restantes: {coins}")
            return 
    

#Resultados 
def mostrar_resultados(jugador1 , jugador2):
    print("\n" + "=" * 40)
    print("RESULTADO FINAL")
    print("=" * 40)

    if jugador1["gano"] and jugador2["gano"]:

        if jugador1["coins"] > jugador2["coins"]:
            print(f"GANA {jugador1['nombre']}")
            print(f"Coins: {jugador1['coins']}")

        elif jugador2["coins"] > jugador1["coins"]:
            print(f"GANA {jugador2['nombre']}")
            print(f"Coins: {jugador2['coins']}")

        else:
            print("¡EMPATE!")
            print(f"Ambos terminaron con {jugador1['coins']} coins.")

    elif jugador1["gano"]:
        print(f"GANA {jugador1['nombre']}")
        print(f"El Jugador 2 no llegó a la meta.")

    elif jugador2["gano"]:
        print(f"GANA {jugador2['nombre']}")
        print(f"El Jugador 1 no llegó a la meta.")

    else:
        print("Ningún jugador llegó a la meta.")

#menu
def menu():
    while True:
        print("\n" + "=" * 40)
        print("MENÚ DE JUEGO LABERINTO 🎮")
        print("=" * 40)
        print("1. Jugar manualmente (2 jugadores)")
        print("2. Modo automático algoritmo BFS")
        print("3. Modo automático algoritmo DFS")
        print("4. Salir")

        opcion = input("\nSelecciona una opción (1-4): ").strip()

        if opcion == "1":
            jugador1 = jugar("Jugador 1")
            jugador2 = jugar("Jugador 2")
            mostrar_resultados(jugador1, jugador2)
        elif opcion == "2":
            jugar_bfs_aut(grafo)
        elif opcion == "3":
            jugar_dfs_aut(grafo)
        elif opcion == "4":
            print("¡Gracias por jugar! 👋")
            break
        else:
            print("Opción inválida. Selecciona una opción entre 1 y 4.")
    print("\n" + "=" * 40)
    print("MENÚ DE JUEGO LABERINTO 🎮")
    print("=" * 40)
    print("1. Jugar manualmente (2 jugadores)")
    print("2. Modo automático algoritmo BFS")
    print("3. Modo automático algoritmo DFS")
    print("4. Salir")

    print()
    opcion = input("Selecciona una opción (1-4): ").strip()

    #opcion 1
    if opcion == "1":
        jugador1 = jugar("Jugador 1")
        jugador2 = jugar("Jugador 2")
        mostrar_resultados(jugador1, jugador2)

    #opcion 2
    elif opcion == "2":
        jugar_bfs_aut( grafo)

    #opcion 3
    elif opcion == "3":
        jugar_dfs_aut( grafo)

    #opcion 4
    elif opcion == "4":
        print("¡Gracias por jugar! 👋")
        exit()

    else:
        print("Opción inválida. Por favor, selecciona una opción válida (1-4).")
menu()  # Volver al menú después de cada acción


