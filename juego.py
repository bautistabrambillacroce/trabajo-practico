"""
Búsqueda del Tesoro en la Plaza Rodríguez Peña (Recoleta, Buenos Aires)
-----------------------------------------------------------------------
La plaza (Callao y Marcelo T. de Alvear) se representa como una cuadrícula de 10x10 (coordenadas x, y de 0 a 9):
  x: 0 = oeste ... 9 = este
  y: 0 = sur   ... 9 = norte

En cada partida el tesoro se esconde en un punto ALEATORIO y los puntos de
referencia de la plaza (fuente, monumento, etc.) entregan pistas distintas.
El jugador visita puntos para leer pistas y luego intenta cavar en el lugar exacto.
"""
import random

TAMANIO = 10

# Puntos de referencia de la Plaza Rodríguez Peña: nombre -> (x, y)
# OJO: las posiciones son aproximadas. Ajustalas según el plano real de la plaza.
PUNTOS = {
    "Fuente 'El sediento'": (5, 5),
    "Monumento a Nicolás Rodríguez Peña": (2, 7),
    "Jacarandá": (8, 8),
    "Juegos inclusivos": (7, 2),
    "Canchas de fútbol tenis": (1, 2),
    "Zona de mascotas": (9, 5),
    "Sector de estar": (3, 4),
    "Esquina Callao y Alvear": (4, 9),
}


class JuegoTesoro:
    def __init__(self, cant_pistas=4, intentos=5, semilla=None):
        self.rng = random.Random(semilla)
        self.intentos_max = intentos
        self.intentos = intentos
        self.terminado = False
        self.gano = False

        # Tesoro en una celda aleatoria que no sea un punto de referencia
        libres = [(x, y) for x in range(TAMANIO) for y in range(TAMANIO)
                  if (x, y) not in PUNTOS.values()]
        self.tesoro = self.rng.choice(libres)

        # Puntos con pista: aleatorios en cada partida
        self.puntos_con_pista = self.rng.sample(list(PUNTOS), cant_pistas)
        self.pistas = {n: self._crear_pista(n) for n in self.puntos_con_pista}
        self.visitados = set()

    # ---------- Pistas ----------
    def _direccion(self, origen):
        dx = self.tesoro[0] - origen[0]
        dy = self.tesoro[1] - origen[1]
        partes = []
        if dy > 0: partes.append("norte")
        if dy < 0: partes.append("sur")
        if dx > 0: partes.append("este")
        if dx < 0: partes.append("oeste")
        return " y al ".join(partes) if partes else "justo ahí"

    def _distancia(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _crear_pista(self, nombre):
        origen = PUNTOS[nombre]
        d = self._distancia(origen, self.tesoro)
        tipo = self.rng.choice(["direccion", "distancia", "ambas"])
        direccion = f"El tesoro está al {self._direccion(origen)} de {nombre}."
        distancia = f"Desde {nombre}, el tesoro está a unos {max(1, d - 1)} a {d + 1} pasos."
        if tipo == "direccion":
            return direccion
        if tipo == "distancia":
            return distancia
        return direccion + " " + distancia

    # ---------- Acciones del jugador ----------
    def listar_puntos(self):
        return list(PUNTOS)

    def visitar(self, nombre):
        """Devuelve la pista de un punto (o un mensaje si no tiene)."""
        self.visitados.add(nombre)
        if nombre in self.pistas:
            return "📜 Pista: " + self.pistas[nombre]
        return "No hay nada interesante acá... probá en otro punto."

    def cavar(self, x, y):
        """Intenta cavar en (x, y). Devuelve un mensaje."""
        if self.terminado:
            return "El juego ya terminó."
        if not (0 <= x < TAMANIO and 0 <= y < TAMANIO):
            return f"Ese lugar está fuera de la plaza (usá números de 0 a {TAMANIO - 1})."

        self.intentos -= 1
        d = self._distancia((x, y), self.tesoro)
        if d == 0:
            self.terminado = self.gano = True
            return "🏆 ¡ENCONTRASTE EL TESORO! ¡Ganaste!"

        if d <= 1:
            calor = "🔥 ¡Quemando! Estás pegado al tesoro."
        elif d <= 3:
            calor = "♨️ Caliente."
        elif d <= 5:
            calor = "🌤️ Tibio."
        else:
            calor = "❄️ Frío."

        if self.intentos == 0:
            self.terminado = True
            return (f"{calor}\n💀 Se acabaron los intentos. "
                    f"El tesoro estaba en ({self.tesoro[0]}, {self.tesoro[1]}).")
        return f"{calor} Te quedan {self.intentos} intentos."


def mostrar_mapa(juego):
    """Dibuja la plaza con los puntos de referencia numerados."""
    nombres = list(PUNTOS)
    print("\n   " + " ".join(str(x) for x in range(TAMANIO)) + "   (x →)")
    for y in range(TAMANIO - 1, -1, -1):
        fila = []
        for x in range(TAMANIO):
            marca = "."
            for i, n in enumerate(nombres, 1):
                if PUNTOS[n] == (x, y):
                    marca = str(i)
            fila.append(marca)
        print(f"{y}  " + " ".join(fila))
    print("(y ↑)\n")
    for i, n in enumerate(nombres, 1):
        print(f"  {i}. {n}")
    print()


def jugar():
    juego = JuegoTesoro()
    nombres = juego.listar_puntos()
    print("🗺️  BÚSQUEDA DEL TESORO EN LA PLAZA RODRÍGUEZ PEÑA 🗺️")
    print("Hay un tesoro escondido en la plaza. Visitá los puntos para leer pistas y")
    print(f"después cavá en el lugar exacto. Tenés {juego.intentos_max} intentos.")
    mostrar_mapa(juego)

    while not juego.terminado:
        op = input("¿Qué hacés? [v] visitar punto  [c] cavar  [m] mapa  [s] salir: ").strip().lower()
        if op == "m":
            mostrar_mapa(juego)
        elif op == "v":
            n = input("Número del punto a visitar: ").strip()
            if n.isdigit() and 1 <= int(n) <= len(nombres):
                print(juego.visitar(nombres[int(n) - 1]))
            else:
                print("Número inválido.")
        elif op == "c":
            try:
                x = int(input("Coordenada x: "))
                y = int(input("Coordenada y: "))
                print(juego.cavar(x, y))
            except ValueError:
                print("Tenés que escribir números.")
        elif op == "s":
            print("¡Hasta la próxima!")
            return
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    jugar()
