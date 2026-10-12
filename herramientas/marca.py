"""Genera los SVG de la marca de IronDeck en marca/.

Uso:  python herramientas/marca.py

La marca es una chapa de acero mate con el yunque calado (un agujero, no una figura montada)
y el calor del temple subiendo hasta la mitad. Dos tamaños de dibujo:
  - detallado (48 px o más): textura mate, remaches, bisel y la pared del corte;
  - simple (32 px o menos): sin textura ni remaches, con el yunque más grande.
Los PNG y los ICO se exportan de estos SVG (cualquier navegador o Inkscape sirve).
Solo usa la biblioteca estándar de Python.
"""
import math
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "marca"

TINTA = "#121820"       # texto y una tinta sobre fondo claro
CLARO = "#e4e9ef"       # texto sobre fondo oscuro

# Yunque inglés en unidades de largo 100 (talón = 100) y alto 46: cuerno cónico cuya cara de abajo
# baja en una sola curva hasta la garganta del cuerpo, mesa, escalón, cara, talón, cintura y patas con arco.
YUNQUE = ("M9.5,6.8 C16,5.6 24,4.6 30,4.2 L37.5,4.2 L37.5,0.6 L38.3,0 L99.2,0 L100,0.8 L100,9.4 "
          "C96,10.3 91,11 87,12.4 C81,14.5 76.5,20 75.5,28 C75,34 78.5,38.5 86.5,40.6 "
          "L88.2,41.2 L89,46 L71,46 C68.5,41.5 50.5,41.5 48,46 L28.5,46 L29.5,41.2 L31,40.6 "
          "C38,38.6 41.6,34 41.6,28 C41.6,22 39,17.8 33.5,15.2 C26,12 17.5,10.2 10.4,9.7 "
          "C8.4,9.5 7.9,7.2 9.5,6.8 Z")
FILO = "M10.6,6.6 C16,5.6 24,4.6 30,4.2 L37.5,4.2 M38.3,0 L99.2,0"   # labio de luz en el borde de arriba del corte

# Posición del yunque dentro de la chapa (escala y traslado), según el tamaño de dibujo
YUNQUE_EN_CHAPA = {True: (0.76, 7.46, 33.52), False: (0.88, 1.0, 30.76)}

# «IRONDECK» en Big Shoulders Stencil Display 800, espaciado 0,04 em, en contornos (no depende de la fuente).
# Unidades de la fuente: alto de mayúsculas 1600, ancho total 7354.0.
PALABRA = "M86 1600V0H345V1600ZM1113.0 1600 964.0 1042H949.0V814H961.0Q1025.0 814 1056.5 784.5Q1088.0 755 1091.0 698Q1094.0 642 1095.0 581.5Q1096.0 521 1095.0 460.5Q1094.0 400 1091.0 344Q1088.0 287 1056.5 257.5Q1025.0 228 961.0 228H952.0V0H961.0Q1163.0 0 1253.0 83.0Q1343.0 166 1349.0 357Q1352.0 421 1352.5 472.5Q1353.0 524 1352.5 574.5Q1352.0 625 1349.0 685Q1341.0 919 1201.0 994L1382.0 1600ZM597.0 1600V0H856.0V1600ZM1917.0 1617Q1743.0 1608 1664.5 1522.5Q1586.0 1437 1582.0 1252Q1579.0 1143 1578.0 1029.0Q1577.0 915 1577.0 799.5Q1577.0 684 1578.0 570.0Q1579.0 456 1582.0 346Q1586.0 162 1664.5 77.0Q1743.0 -8 1917.0 -17V198Q1880.0 208 1861.5 233.0Q1843.0 258 1841.0 299Q1837.0 412 1834.5 539.0Q1832.0 666 1832.0 798.5Q1832.0 931 1834.5 1058.5Q1837.0 1186 1841.0 1299Q1843.0 1341 1861.5 1366.5Q1880.0 1392 1917.0 1402ZM2014.0 1617V1402Q2050.0 1392 2068.5 1366.5Q2087.0 1341 2088.0 1299Q2093.0 1186 2095.0 1058.5Q2097.0 931 2096.5 798.5Q2096.0 666 2094.5 539.0Q2093.0 412 2088.0 299Q2087.0 258 2068.5 233.0Q2050.0 208 2014.0 198V-17Q2187.0 -8 2263.0 78.0Q2339.0 164 2345.0 346Q2348.0 457 2350.0 571.0Q2352.0 685 2352.0 800.5Q2352.0 916 2350.0 1029.5Q2348.0 1143 2345.0 1252Q2339.0 1435 2263.0 1521.0Q2187.0 1607 2014.0 1617ZM3031.0 1600 2921.0 1064 2829.0 226H2592.0V0H2978.0L3086.0 509L3203.0 1372H3435.0V1600ZM2592.0 1600V319H2759.0L2820.0 1066L2842.0 1600ZM3270.0 1279 3198.0 517 3185.0 0H3435.0V1279ZM3688.0 1600V0H3947.0V1600ZM4043.0 1600V1372H4056.0Q4121.0 1372 4153.5 1342.0Q4186.0 1312 4187.0 1255Q4190.0 1140 4191.5 1026.5Q4193.0 913 4193.0 799.0Q4193.0 685 4191.5 571.0Q4190.0 457 4187.0 344Q4186.0 287 4153.5 257.5Q4121.0 228 4057.0 228H4043.0V0H4057.0Q4260.0 0 4351.0 87.0Q4442.0 174 4445.0 374Q4448.0 526 4449.0 662.5Q4450.0 799 4449.0 935.5Q4448.0 1072 4445.0 1224Q4442.0 1425 4351.0 1512.5Q4260.0 1600 4056.0 1600ZM4690.0 1600V0H4949.0V1600ZM5044.0 1600V1372H5322.0V1600ZM5044.0 902V674H5302.0V902ZM5044.0 228V0H5322.0V228ZM5860.0 1617Q5681.0 1608 5605.5 1522.5Q5530.0 1437 5526.0 1252Q5524.0 1154 5523.0 1038.0Q5522.0 922 5522.0 800.0Q5522.0 678 5523.0 561.5Q5524.0 445 5526.0 346Q5529.0 186 5607.5 90.5Q5686.0 -5 5860.0 -16V198Q5823.0 208 5804.5 233.5Q5786.0 259 5784.0 300Q5780.0 416 5778.5 543.0Q5777.0 670 5777.0 800.0Q5777.0 930 5778.5 1056.5Q5780.0 1183 5784.0 1299Q5786.0 1341 5804.5 1367.0Q5823.0 1393 5860.0 1402ZM5956.0 1617V1402Q5994.0 1392 6013.5 1366.0Q6033.0 1340 6034.0 1299Q6035.0 1258 6035.5 1205.0Q6036.0 1152 6035.5 1099.0Q6035.0 1046 6034.0 1006H6292.0Q6294.0 1063 6294.0 1128.5Q6294.0 1194 6292.0 1252Q6287.0 1436 6208.5 1521.5Q6130.0 1607 5956.0 1617ZM6024.0 589Q6025.0 548 6026.0 496.5Q6027.0 445 6027.0 393.0Q6027.0 341 6026.0 300Q6025.0 260 6007.5 234.5Q5990.0 209 5956.0 199V-17Q6125.0 -7 6202.0 78.5Q6279.0 164 6284.0 347Q6285.0 382 6285.0 425.0Q6285.0 468 6284.0 511.5Q6283.0 555 6282.0 589ZM6523.0 1600V756H6799.0L6902.0 377L7038.0 0H7320.0L6787.0 1309V1600ZM7073.0 1600 6945.0 1150 7096.0 786 7336.0 1600ZM6523.0 673V0H6798.0L6795.0 378L6746.0 673Z"
PALABRA_ANCHO, PALABRA_ALTO = 7354.0, 1600


class Ids:
    """Ids únicos y estables dentro de un archivo."""
    def __init__(self):
        self.n = 0

    def __call__(self, base):
        self.n += 1
        return f"{base}{self.n}"


def paradas(lista):
    return "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in lista)


def lineal(ids, lista, x1=0, y1=0, x2=1, y2=0, espacio=False):
    gid = ids("g")
    u = ' gradientUnits="userSpaceOnUse"' if espacio else ""
    return gid, f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{paradas(lista)}</linearGradient>'


def radial(ids, lista, cx, cy, r, extra=""):
    gid = ids("r")
    return gid, f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}" gradientUnits="userSpaceOnUse"{extra}>{paradas(lista)}</radialGradient>'


def squircle(a=47.0, n=5.0, pasos=160, cx=50.0, cy=50.0):
    """Superelipse: la esquina suave de los iconos de Windows 11 y macOS."""
    pts = []
    for k in range(pasos):
        t = 2 * math.pi * k / pasos
        c, s = math.cos(t), math.sin(t)
        pts.append(f"{cx + a * math.copysign(abs(c) ** (2 / n), c):.2f},{cy + a * math.copysign(abs(s) ** (2 / n), s):.2f}")
    return "M" + " L".join(pts) + " Z"


CHAPA = squircle()
CHAPA_BISEL = squircle(a=45.6)


def mover_ruta(ruta, s, tx, ty):
    """Aplica escala y traslado a una ruta de pares absolutos x,y (solo M, L, C, Z)."""
    return re.sub(r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)",
                  lambda m: f"{float(m.group(1)) * s + tx:.2f},{float(m.group(2)) * s + ty:.2f}", ruta)


def mate(ids, sid):
    """Textura mate (granallado): grano fino claro y oscuro y un moteado suave."""
    f1, f2, f3, cid = ids("f"), ids("f"), ids("f"), ids("c")
    defs = (f'<filter id="{f1}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="1.7" numOctaves="3" seed="7" stitchTiles="stitch"/>'
            f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.11 -0.02"/></filter>'
            f'<filter id="{f2}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="1.3" numOctaves="2" seed="13" stitchTiles="stitch"/>'
            f'<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.16 -0.03"/></filter>'
            f'<filter id="{f3}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="2" seed="3" stitchTiles="stitch"/>'
            f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.10 -0.03"/></filter>'
            f'<clipPath id="{cid}"><use xlink:href="#{sid}"/></clipPath>')
    capa = (f'<g clip-path="url(#{cid})"><rect width="100" height="100" filter="url(#{f3})"/>'
            f'<rect width="100" height="100" filter="url(#{f1})"/><rect width="100" height="100" filter="url(#{f2})"/></g>')
    return defs, capa


def agujero(ids, detalle):
    """El yunque calado: adentro, la profundidad oscura; abajo, la pared del corte iluminada
    (el grosor de la chapa, tibia por el calor); arriba, el labio de luz. Sin sombra: no está montado."""
    s, tx, ty = YUNQUE_EN_CHAPA[detalle]
    hid = ids("h")
    gp, dp = lineal(ids, [(0, "#8b939d", 1), (0.6, "#8f8a82", 1), (1, "#c09763", 1)], 0, 8, 0, 46, True)
    gf, df = lineal(ids, [(0, "#06080a", 1), (1, "#0d1014", 1)], 0, 0, 0, 46, True)
    paso = 2.0 if detalle else 1.6
    defs = f'<clipPath id="{hid}"><path d="{YUNQUE}"/></clipPath>{dp}{df}'
    cuerpo = (f'<g transform="translate({tx} {ty}) scale({s})">'
              f'<path d="{YUNQUE}" fill="url(#{gp})"/>'
              f'<g clip-path="url(#{hid})"><path d="{YUNQUE}" transform="translate(0 {-paso})" fill="url(#{gf})"/></g>'
              f'<path d="{FILO}" fill="none" stroke="#ffffff" stroke-opacity="0.22" stroke-width="{0.7 if detalle else 1.4}" stroke-linecap="round"/></g>')
    return defs, cuerpo


def chapa_interior(ids, detalle=True):
    """Contenido de la chapa en un lienzo de 100 × 100 (sin la etiqueta <svg>)."""
    sid = ids("s")
    defs = f'<path id="{sid}" d="{CHAPA}"/>'
    gb, d = lineal(ids, [(0, "#525962", 1), (0.55, "#3d434a", 1), (1, "#30353b", 1)], 0.25, 0, 0.75, 1); defs += d
    calor = [(0, "#405584", 0.95), (0.2, "#4c5f8a", 0.9), (0.36, "#6c5570", 0.88), (0.52, "#946748", 0.86),
             (0.68, "#bf9c64", 0.78), (0.8, "#a89a80", 0.35), (0.9, "#7d7a76", 0)]
    rc, d = radial(ids, calor, 50, 100, 66, ' gradientTransform="translate(50 100) scale(1.6 1) translate(-50 -100)"'); defs += d
    rv, d = radial(ids, [(0, "#000000", 0), (0.7, "#000000", 0), (1, "#000000", 0.22)], 50, 46, 66); defs += d
    gbis, d = lineal(ids, [(0, "#ffffff", 0.32), (0.16, "#ffffff", 0.06), (0.8, "#000000", 0), (1, "#000000", 0.4)], 0, 0, 0, 1); defs += d
    textura = remaches = ""
    if detalle:
        d, textura = mate(ids, sid); defs += d
        for x, y in ((14.5, 14.5), (85.5, 14.5), (14.5, 85.5), (85.5, 85.5)):
            gr, d = lineal(ids, [(0, "#7a828c", 1), (0.5, "#4a5159", 1), (1, "#2a2f35", 1)], 0, 0, 1, 1); defs += d
            remaches += (f'<circle cx="{x}" cy="{y}" r="3" fill="#000000" fill-opacity="0.3"/>'
                         f'<circle cx="{x}" cy="{y}" r="2.1" fill="url(#{gr})"/>'
                         f'<circle cx="{x - 0.6:.1f}" cy="{y - 0.7:.1f}" r="0.5" fill="#ffffff" fill-opacity="0.3"/>')
    d, hueco = agujero(ids, detalle); defs += d
    usa = lambda extra: f'<use xlink:href="#{sid}" {extra}/>'
    return (f'<defs>{defs}</defs>{usa(f"fill=\"url(#{gb})\"")}{usa(f"fill=\"url(#{rc})\"")}'
            f'{usa(f"fill=\"url(#{rv})\"")}{textura}'
            f'<path d="{CHAPA_BISEL}" fill="none" stroke="url(#{gbis})" stroke-width="1.1"/>'
            f'{usa("fill=\"none\" stroke=\"#1b2026\" stroke-width=\"0.9\"")}{remaches}{hueco}')


def svg(ancho, alto, caja, contenido, titulo="IronDeck"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{ancho}" height="{alto}" viewBox="{caja}" role="img" aria-label="{titulo}">'
            f'<title>{titulo}</title>{contenido}</svg>\n')


def una_tinta(color):
    """Una sola tinta: la chapa llena y el yunque como agujero de verdad (se ve el fondo)."""
    s, tx, ty = YUNQUE_EN_CHAPA[False]
    return f'<path fill="{color}" fill-rule="evenodd" d="{CHAPA} {mover_ruta(YUNQUE, s, tx, ty)}"/>'


def horizontal(ids, color_texto):
    """Icono simple + «IRONDECK»: la versión para cabeceras, documentos y firmas."""
    esc = 44 / PALABRA_ALTO
    x_texto = 124
    ancho = x_texto + PALABRA_ANCHO * esc + 2
    contenido = (f'<svg x="0" y="0" width="100" height="100" viewBox="0 0 100 100">{chapa_interior(ids, False)}</svg>'
                 f'<path fill="{color_texto}" transform="translate({x_texto} 28) scale({esc:.5f})" d="{PALABRA}"/>')
    return ancho, contenido


def escribir(nombre, texto):
    (DESTINO / nombre).write_text(texto, encoding="utf-8", newline="\n")


def main():
    DESTINO.mkdir(exist_ok=True)
    escribir("irondeck-icono.svg", svg(512, 512, "0 0 100 100", chapa_interior(Ids(), True)))
    escribir("irondeck-icono-simple.svg", svg(32, 32, "0 0 100 100", chapa_interior(Ids(), False)))
    escribir("irondeck-una-tinta.svg", svg(512, 512, "0 0 100 100", una_tinta(TINTA)))
    escribir("irondeck-una-tinta-blanca.svg", svg(512, 512, "0 0 100 100", una_tinta("#ffffff")))
    escribir("irondeck-yunque.svg", svg(480, 240, "6 -2 96 50", f'<path fill="{TINTA}" d="{YUNQUE}"/>', "Yunque de IronDeck"))
    for nombre, color in (("irondeck-horizontal.svg", TINTA), ("irondeck-horizontal-clara.svg", CLARO)):
        ancho, contenido = horizontal(Ids(), color)
        escribir(nombre, svg(round(ancho * 1.28), 128, f"0 0 {ancho:.1f} 100", contenido))
    print("Listo: SVG de la marca en marca/")


if __name__ == "__main__":
    main()
