"""Arma el sitio de IronDeck a partir de fuente/, sitio.json y novedades.json.

Uso:
    python herramientas/armar.py                     # escribe index.html, en/index.html, las páginas legales y sitemap.xml
    python herramientas/armar.py --vista-previa DIR  # además, las vistas previas de claude.ai (los dos idiomas en una página)

Las páginas legales salen de fuente/legal/. Mientras falte en sitio.json → legal el titular, el correo o la fecha
de vigencia, o mientras esa fecha sea futura, no se publican (solo se ven, como borrador, en la vista previa) y
la lista de espera, las aportaciones y la analítica quedan apagadas: no se recogen datos sin un aviso vigente.

Solo usa la biblioteca estándar de Python 3.8 o más nuevo.
"""
import datetime
import html
import json
import pathlib
import re
import urllib.parse
import sys
from html.parser import HTMLParser

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IDIOMAS = ("es", "en")
VACIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

FUENTES = [
    ("Inter Tight", 400, "inter-tight-latin-400-normal.woff2"),
    ("Inter Tight", 500, "inter-tight-latin-500-normal.woff2"),
    ("Inter Tight", 600, "inter-tight-latin-600-normal.woff2"),
    ("Big Shoulders Display", 700, "big-shoulders-display-latin-700-normal.woff2"),
    ("Big Shoulders Display", 800, "big-shoulders-display-latin-800-normal.woff2"),
    ("Big Shoulders Stencil Display", 800, "big-shoulders-stencil-display-latin-800-normal.woff2"),
    ("IBM Plex Mono", 400, "ibm-plex-mono-latin-400-normal.woff2"),
    ("IBM Plex Mono", 500, "ibm-plex-mono-latin-500-normal.woff2"),
]
GOOGLE_FONTS = ("https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600"
                "&family=Big+Shoulders+Display:wght@700;800&family=Big+Shoulders+Stencil+Display:wght@800"
                "&family=IBM+Plex+Mono:wght@400;500&display=swap")

MESES = {
    "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}
MESES_LARGOS = {
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
           "noviembre", "diciembre"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"],
}
LOCALE_OG = {"es": "es_LA", "en": "en_US"}

# Páginas legales: clave → por idioma, (archivo, título, descripción). En inglés viven dentro de en/.
LEGALES = {
    "privacidad": {
        "es": ("privacidad.html", "Aviso de privacidad",
               "Qué datos trata IronDeck en su sitio, su lista de espera, las aportaciones y la beta, y qué derechos tienes."),
        "en": ("privacy.html", "Privacy notice",
               "What data IronDeck handles on its site, waitlist, contributions and beta, and what rights you have."),
    },
    "terminos": {
        "es": ("terminos.html", "Términos de uso del sitio",
               "Las condiciones para usar el sitio de IronDeck, su lista de espera y las aportaciones."),
        "en": ("terms.html", "Website terms of use",
               "The conditions for using IronDeck's website, waitlist and contributions."),
    },
    "beta": {
        "es": ("terminos-beta.html", "Términos de la beta",
               "Las condiciones para probar la versión beta del programa IronDeck."),
        "en": ("beta-terms.html", "Beta terms",
               "The conditions for testing the beta version of the IronDeck program."),
    },
}
PENDIENTE = {
    "es": {"titular": "[titular pendiente]", "correo": "[correo pendiente]", "fecha": "[fecha pendiente]"},
    "en": {"titular": "[owner pending]", "correo": "[email pending]", "fecha": "[date pending]"},
}
RECOGEN_DATOS = ("listaEspera", "kofi", "sponsors")


class Filtro(HTMLParser):
    """Deja solo un idioma y quita los bloques que dependen de un enlace vacío."""

    def __init__(self, idioma, enlaces):
        super().__init__(convert_charrefs=False)
        # idioma None: deja los dos idiomas con sus clases (vista previa con cambio de idioma en la misma página)
        self.bilingue = idioma is None
        self.otro = None if self.bilingue else ("en" if idioma == "es" else "es")
        self.idioma = idioma
        self.enlaces = enlaces
        self.salida = []
        self.saltando = 0
        self.pila = []

    def _quitar(self, attrs):
        clases = (attrs.get("class") or "").split()
        if self.otro in clases:
            return True
        si, no = attrs.get("data-si"), attrs.get("data-no")
        if si is not None and not self.enlaces.get(si):
            return True
        if no is not None and self.enlaces.get(no):
            return True
        return False

    def _etiqueta(self, tag, attrs, cerrar=False):
        partes = [tag]
        for nombre, valor in attrs:
            if nombre in ("data-si", "data-no"):
                continue
            if nombre == "class" and not self.bilingue:
                valor = " ".join(c for c in (valor or "").split() if c not in IDIOMAS)
                if not valor:
                    continue
            if valor is None:
                partes.append(nombre)
            else:
                partes.append(f'{nombre}="{html.escape(valor, quote=True)}"')
        return "<" + " ".join(partes) + (" />" if cerrar else ">")

    def handle_starttag(self, tag, attrs):
        if self.saltando:
            if tag not in VACIOS:
                self.saltando += 1
            return
        dic = dict(attrs)
        if self._quitar(dic):
            if tag not in VACIOS:
                self.saltando = 1
            return
        limpios = [(n, v) for n, v in attrs if n not in ("data-si", "data-no")]
        sin_atributos = not self.bilingue and tag == "span" and bool(limpios) and all(
            n == "class" and not [c for c in (v or "").split() if c not in IDIOMAS] for n, v in limpios)
        if tag not in VACIOS:
            self.pila.append(not sin_atributos)
        if not sin_atributos:
            self.salida.append(self._etiqueta(tag, attrs))

    def handle_startendtag(self, tag, attrs):
        if self.saltando or self._quitar(dict(attrs)):
            return
        self.salida.append(self._etiqueta(tag, attrs, cerrar=True))

    def handle_endtag(self, tag):
        if self.saltando:
            if tag not in VACIOS:
                self.saltando -= 1
            return
        if tag in VACIOS:
            return
        emitida = self.pila.pop() if self.pila else True
        if emitida:
            self.salida.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.saltando:
            self.salida.append(data)

    def handle_entityref(self, name):
        if not self.saltando:
            self.salida.append(f"&{name};")

    def handle_charref(self, name):
        if not self.saltando:
            self.salida.append(f"&#{name};")

    def handle_comment(self, data):
        if not self.saltando:
            self.salida.append(f"<!--{data}-->")


def fecha_texto(fecha, idioma):
    partes = [int(p) for p in str(fecha).split("-")]
    if len(partes) == 3:
        anio, mes, dia = partes
        if idioma == "es":
            return f"{dia} {MESES['es'][mes - 1]} {anio}"
        return f"{MESES['en'][mes - 1]} {dia}, {anio}"
    anio, mes = partes[:2]
    return f"{MESES[idioma][mes - 1]} {anio}"


# Novedades que se ven sin abrir «Ver las novedades anteriores»
A_LA_VISTA = 3


def novedades_html(novedades, idioma):
    if idioma is None:
        dos = lambda f: "".join(f'<span class="{i}">{html.escape(f(i))}</span>' for i in IDIOMAS)
        return "\n".join(
            "        <li>"
            f'<time datetime="{html.escape(str(n["fecha"]))}">{dos(lambda i: fecha_texto(n["fecha"], i))}</time>'
            f'<div><h3>{dos(lambda i: n["titulo"][i])}</h3><p>{dos(lambda i: n["texto"][i])}</p></div>'
            "</li>" for n in novedades)
    filas = []
    for n in novedades:
        filas.append(
            "        <li>"
            f'<time datetime="{html.escape(str(n["fecha"]))}">{html.escape(fecha_texto(n["fecha"], idioma))}</time>'
            f'<div><h3>{html.escape(n["titulo"][idioma])}</h3><p>{html.escape(n["texto"][idioma])}</p></div>'
            "</li>")
    return "\n".join(filas)


def css_fuentes(prefijo):
    reglas = []
    for familia, peso, archivo in FUENTES:
        reglas.append(
            f'@font-face{{font-family:"{familia}";font-style:normal;font-weight:{peso};font-display:swap;'
            f'src:url("{prefijo}fuentes/{archivo}") format("woff2")}}')
    return "\n".join(reglas)


def datos_legales(sitio):
    """Lee sitio.json → legal y dice si el aviso de privacidad y los términos están completos."""
    legal = sitio.get("legal") or {}
    titular = (legal.get("titular") or "").strip()
    correo = (legal.get("correo") or "").strip()
    vigencia = (legal.get("vigencia") or "").strip()
    if correo and not re.fullmatch(r"[^@\s<>\"]+@[^@\s<>\"]+\.[A-Za-z]{2,}", correo):
        sys.exit("El correo de «legal» no parece un correo válido")
    futura = False
    if vigencia:
        try:
            futura = datetime.date.fromisoformat(vigencia) > datetime.date.today()
        except ValueError:
            sys.exit("La vigencia de «legal» va como AAAA-MM-DD, por ejemplo 2026-10-20")
    return {"titular": titular, "correo": correo, "vigencia": vigencia, "futura": futura,
            "listo": bool(titular and correo and vigencia) and not futura}


def con_legal(sitio):
    """Copia de sitio.json con lo que recoge datos apagado si los textos legales no están completos."""
    efectivo = json.loads(json.dumps(sitio))
    legal = datos_legales(sitio)
    legal["apagados"] = []
    if not legal["listo"]:
        for clave in RECOGEN_DATOS:
            if efectivo["enlaces"].get(clave):
                legal["apagados"].append(clave)
                efectivo["enlaces"][clave] = ""
        if efectivo.get("analiticaCloudflare"):
            legal["apagados"].append("analiticaCloudflare")
            efectivo["analiticaCloudflare"] = ""
    efectivo["_legal"] = legal
    return efectivo


def lista_prellenada(sitio, idioma):
    """Enlace al formulario con las respuestas que la página ya sabe (el idioma) marcadas de antemano."""
    corto = sitio["enlaces"]["listaEspera"]
    form = sitio.get("listaEsperaFormulario") or {}
    if not corto or not form.get("base"):
        return corto
    pares = [(campo, valores[idioma]) for campo, valores in form.get("campos", {}).items() if valores.get(idioma)]
    if not pares:
        return corto
    return form["base"] + "?usp=pp_url&" + urllib.parse.urlencode(pares)


def cuerpo(idioma, sitio, novedades, otro_enlace, raiz=""):
    fuente = (RAIZ / "fuente" / "pagina.html").read_text(encoding="utf-8")
    enlaces = sitio["enlaces"]
    condiciones = dict(enlaces, analitica=sitio.get("analiticaCloudflare", ""),
                       legal="si" if sitio["_legal"]["listo"] else "",
                       masNovedades="si" if len(novedades) > A_LA_VISTA else "")
    filtro = Filtro(idioma, condiciones)
    filtro.feed(fuente)
    filtro.close()
    texto = "".join(filtro.salida)
    texto = texto.replace("<!--NOVEDADES-->", novedades_html(novedades[:A_LA_VISTA], idioma))
    texto = texto.replace("<!--NOVEDADES-RESTO-->", novedades_html(novedades[A_LA_VISTA:], idioma))

    def poner(m):
        clave = m.group(1)
        if clave == "otro":
            return otro_enlace
        if clave == "raiz":
            return raiz
        if clave == "copyright":
            legal = sitio["_legal"]
            return html.escape(legal["titular"]) if legal["listo"] else "DwladimirL"
        tipo, nombre = clave.split(":", 1)
        if tipo == "url":
            if nombre == "listaEspera" and idioma:
                return html.escape(lista_prellenada(sitio, idioma), quote=True)
            return html.escape(sitio["enlaces"][nombre], quote=True)
        if tipo == "texto":
            return html.escape(sitio["seo"][idioma or "es"][nombre], quote=True)
        raise KeyError(clave)

    texto = re.sub(r"\{\{([^}]+)\}\}", poner, texto)
    if "{{" in texto:
        raise ValueError("Quedó un marcador sin reemplazar")
    texto = re.sub(r"\n[ \t]+(?=\n)", "\n", texto)
    return re.sub(r"\n{3,}", "\n\n", texto)


def preguntas(contenido):
    """Saca las preguntas frecuentes ya filtradas por idioma, para los datos estructurados."""
    seccion = re.search(r'id="preguntas".*?</section>', contenido, re.S)
    if not seccion:
        return []
    limpiar = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
    return [(limpiar(q), limpiar(a)) for q, a in re.findall(r"<h3>(.*?)</h3>(?:</summary>)?<p>(.*?)</p>", seccion.group(0), re.S)]


def datos_estructurados(idioma, sitio, url, contenido):
    seo = sitio["seo"][idioma]
    datos = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": sitio["base"] + "#sitio", "url": sitio["base"], "name": "IronDeck",
             "inLanguage": ["es", "en"], "image": sitio["base"] + "marca/png/irondeck-512.png"},
            {"@type": "SoftwareApplication", "name": "IronDeck", "url": url, "inLanguage": idioma,
             "applicationCategory": "DeveloperApplication", "operatingSystem": "Windows",
             "description": seo["descripcion"], "image": sitio["base"] + "marca/png/irondeck-512.png",
             "author": {"@type": "Person", "name": sitio["_legal"]["titular"] or "DwladimirL",
                        "alternateName": "DwladimirL", "url": sitio["enlaces"]["autor"],
                        "sameAs": [sitio["enlaces"]["autor"]]},
             "sameAs": [sitio["enlaces"]["github"]]},
        ],
    }
    faq = preguntas(contenido)
    if faq:
        datos["@graph"].append({"@type": "FAQPage", "inLanguage": idioma, "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def pagina_completa(idioma, sitio, novedades, css, otro_enlace=None):
    base = sitio["base"]
    url = base if idioma == "es" else base + "en/"
    prefijo = "" if idioma == "es" else "../"
    seo = sitio["seo"][idioma]
    otro_idioma = "en" if idioma == "es" else "es"
    if otro_enlace is None:
        otro_enlace = "en/index.html" if idioma == "es" else "../index.html"
    contenido = cuerpo(idioma, sitio, novedades, otro_enlace, prefijo)
    e = lambda s: html.escape(s, quote=True)
    imagen = base + seo["imagen"]
    fuentes = (f'<link rel="preload" href="{prefijo}fuentes/big-shoulders-display-latin-800-normal.woff2" '
               f'as="font" type="font/woff2" crossorigin>\n'
               f'<link rel="preload" href="{prefijo}fuentes/inter-tight-latin-400-normal.woff2" '
               f'as="font" type="font/woff2" crossorigin>')
    estilo = css_fuentes(prefijo) + "\n" + css
    verificacion = ""
    if sitio.get("googleVerificacion"):
        verificacion = f'\n<meta name="google-site-verification" content="{e(sitio["googleVerificacion"])}">'
    token = sitio.get("analiticaCloudflare", "")
    if token:
        if not re.fullmatch(r"[A-Za-z0-9]+", token):
            sys.exit("El token de analiticaCloudflare solo lleva letras y números")
        verificacion += ("\n<script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
                         f"data-cf-beacon='{{\"token\": \"{token}\"}}'></script>")
    return f"""<!doctype html>
<html lang="{idioma}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(seo["titulo"])}</title>
<meta name="description" content="{e(seo["descripcion"])}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="es" href="{base}">
<link rel="alternate" hreflang="en" href="{base}en/">
<link rel="alternate" hreflang="x-default" href="{base}en/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="IronDeck">
<meta property="og:title" content="{e(seo["titulo"])}">
<meta property="og:description" content="{e(seo["descripcion"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{imagen}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(seo["titulo"])}">
<meta property="og:locale" content="{LOCALE_OG[idioma]}">
<meta property="og:locale:alternate" content="{LOCALE_OG[otro_idioma]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(seo["titulo"])}">
<meta name="twitter:description" content="{e(seo["descripcion"])}">
<meta name="twitter:image" content="{imagen}">
<meta name="twitter:image:alt" content="{e(seo["titulo"])}">
<meta name="theme-color" content="#151b23">{verificacion}
<link rel="icon" href="{prefijo}favicon.ico" sizes="32x32">
<link rel="icon" href="{prefijo}marca/irondeck-icono-simple.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{prefijo}apple-touch-icon.png">
{fuentes}
<style>
{estilo}
</style>
<script type="application/ld+json">{datos_estructurados(idioma, sitio, url, contenido)}</script>
</head>
<body>
{contenido}
</body>
</html>
"""


def fecha_larga(fecha, idioma):
    d = datetime.date.fromisoformat(fecha)
    if idioma == "es":
        return f"{d.day} de {MESES_LARGOS['es'][d.month - 1]} de {d.year}"
    return f"{MESES_LARGOS['en'][d.month - 1]} {d.day}, {d.year}"


def marcas_legales(texto, idioma, legal, enlace_doc):
    """Pone el titular, el correo y la fecha en un texto de un solo idioma; lo que falta queda marcado."""
    falta = lambda c: f'<mark>{PENDIENTE[idioma][c]}</mark>'
    titular = html.escape(legal["titular"]) if legal["titular"] else falta("titular")
    if legal["correo"]:
        c = html.escape(legal["correo"], quote=True)
        contacto = f'<a href="mailto:{c}">{c}</a>'
    else:
        contacto = falta("correo")
    fecha = fecha_larga(legal["vigencia"], idioma) if legal["vigencia"] else falta("fecha")
    texto = texto.replace("{{legal:titular}}", titular).replace("{{legal:contacto}}", contacto)
    texto = texto.replace(f"{{{{fecha:{idioma}}}}}", fecha)
    return re.sub(r"\{\{doc:([a-z]+)\}\}", lambda m: enlace_doc(m.group(1), idioma), texto)


def documento_legal(clave, legal, enlace_doc, historial):
    """El texto de un documento legal con sus marcas puestas en cada idioma (los dos idiomas, cada uno en su div)."""
    fuente = (RAIZ / "fuente" / "legal" / f"{clave}.html").read_text(encoding="utf-8")
    corte = '<div class="en" lang="en">'
    if fuente.count(corte) != 1:
        raise ValueError(f"fuente/legal/{clave}.html tiene que tener un bloque en español y luego uno en inglés")
    es, en = fuente.split(corte)
    texto = marcas_legales(es, "es", legal, enlace_doc) + corte + marcas_legales(en, "en", legal, enlace_doc)
    return texto.replace("{{historial}}", html.escape(historial, quote=True))


def historial_legal(sitio):
    return sitio["enlaces"]["github"] + "/commits/main/fuente/legal"


BORRADOR = ('<p class="legal-borrador" role="note"><span class="es">Borrador: falta completar el titular, el correo de contacto '
            'o la fecha de vigencia. Hasta entonces estos textos no se publican en el sitio.</span>'
            '<span class="en">Draft: the owner, contact email or effective date is still missing. Until then these texts '
            'aren\'t published on the site.</span></p>')


def filtrar(texto, idioma, sitio):
    condiciones = dict(sitio["enlaces"], analitica=sitio.get("analiticaCloudflare", ""),
                       legal="si" if sitio["_legal"]["listo"] else "")
    filtro = Filtro(idioma, condiciones)
    filtro.feed(texto)
    filtro.close()
    return "".join(filtro.salida)


def cuerpo_legal(clave, idioma, sitio, otro_enlace, raiz):
    legal = sitio["_legal"]
    enlace_doc = lambda c, i: LEGALES[c][i][0]
    marco = (RAIZ / "fuente" / "legal" / "marco.html").read_text(encoding="utf-8")
    marco = marco.replace("<!--DOCUMENTO-->", documento_legal(clave, legal, enlace_doc, historial_legal(sitio)))
    marco = marco.replace("<!--BORRADOR-->", "" if legal["listo"] else BORRADOR)
    for c in LEGALES:
        marco = marco.replace(f"{{{{actual:{c}}}}}", ' aria-current="page"' if c == clave else "")
    texto = filtrar(marco, idioma, sitio)
    reemplazos = {"{{inicio}}": "index.html", "{{otro}}": otro_enlace, "{{raiz}}": raiz,
                  "{{titulo:es}}": LEGALES[clave]["es"][1], "{{titulo:en}}": LEGALES[clave]["en"][1]}
    for a, b in reemplazos.items():
        texto = texto.replace(a, b)
    texto = re.sub(r"\{\{doc:([a-z]+)\}\}", lambda m: enlace_doc(m.group(1), idioma), texto)
    if "{{" in texto:
        raise ValueError(f"Quedó un marcador sin reemplazar en la página legal «{clave}»")
    return re.sub(r"\n{3,}", "\n\n", texto)


def pagina_legal(clave, idioma, sitio, css):
    base = sitio["base"]
    legal = sitio["_legal"]
    archivo, titulo, descripcion = LEGALES[clave][idioma]
    otro_idioma = "en" if idioma == "es" else "es"
    prefijo = "" if idioma == "es" else "../"
    carpeta = {"es": "", "en": "en/"}
    url = base + carpeta[idioma] + archivo
    otro_enlace = ("en/" if idioma == "es" else "../") + LEGALES[clave][otro_idioma][0]
    contenido = cuerpo_legal(clave, idioma, sitio, otro_enlace, prefijo)
    e = lambda s: html.escape(s, quote=True)
    robots = "" if legal["listo"] else '\n<meta name="robots" content="noindex">'
    alternos = "".join(f'\n<link rel="alternate" hreflang="{i}" href="{base}{carpeta[i]}{LEGALES[clave][i][0]}">'
                       for i in IDIOMAS)
    alternos += f'\n<link rel="alternate" hreflang="x-default" href="{base}en/{LEGALES[clave]["en"][0]}">'
    return f"""<!doctype html>
<html lang="{idioma}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)} | IronDeck</title>
<meta name="description" content="{e(descripcion)}">{robots}
<link rel="canonical" href="{url}">{alternos}
<meta name="theme-color" content="#151b23">
<link rel="icon" href="{prefijo}favicon.ico" sizes="32x32">
<link rel="icon" href="{prefijo}marca/irondeck-icono-simple.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{prefijo}apple-touch-icon.png">
<link rel="preload" href="{prefijo}fuentes/inter-tight-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>
{css_fuentes(prefijo)}
{css}
</style>
</head>
<body>
{contenido}
</body>
</html>
"""


def fragmento_legal(sitio, css):
    """Vista previa de claude.ai de los tres textos legales, en los dos idiomas, con el cambio en la misma página."""
    legal = sitio["_legal"]
    enlace_doc = lambda c, i: f"#legal-{c}"
    nav = "".join(f'<a href="#legal-{c}"><span class="es">{LEGALES[c]["es"][1]}</span>'
                  f'<span class="en">{LEGALES[c]["en"][1]}</span></a>' for c in LEGALES)
    secciones = "".join(
        f'<section class="legal-seccion" id="legal-{c}"><h1><span class="es">{LEGALES[c]["es"][1]}</span>'
        f'<span class="en">{LEGALES[c]["en"][1]}</span></h1>\n{documento_legal(c, legal, enlace_doc, historial_legal(sitio))}</section>\n'
        for c in LEGALES)
    pagina = f"""<a class="skip" href="#contenido"><span class="es">Saltar al contenido</span><span class="en">Skip to content</span></a>
<div class="temper-edge" aria-hidden="true"></div>
<header class="top legal-top">
  <div class="frame top-inner">
    <span class="mark"><img class="mark-icono" src="marca/irondeck-icono-simple.svg" alt="" width="28" height="28">IRONDECK</span>
    <a class="lang-link es" href="#idioma" hreflang="en" lang="en">English</a>
    <a class="lang-link en" href="#idioma" hreflang="es" lang="es">Español</a>
  </div>
</header>
<main id="contenido" class="legal">
  <div class="frame legal-frame">
    {"" if legal["listo"] else BORRADOR}
    <nav class="legal-nav legal-indice" aria-label="Legal">{nav}</nav>
    {secciones}
  </div>
</main>
"""
    cuerpo_html = filtrar(pagina, None, sitio)
    if "{{" in cuerpo_html:
        raise ValueError("Quedó un marcador sin reemplazar en la vista previa legal")
    return (f"<title>IronDeck · Textos legales</title>\n<link rel=\"stylesheet\" href=\"{GOOGLE_FONTS}\">\n"
            f"<style>\n{css}\n</style>\n{CAMBIO_IDIOMA}\n{cuerpo_html}\n")


CAMBIO_IDIOMA = """<style>html:not([data-idioma="en"]) .en{display:none!important}html[data-idioma="en"] .es{display:none!important}</style>
<script>(function(){var h=document.documentElement;function poner(l){h.setAttribute("data-idioma",l);h.lang=l;try{localStorage.setItem("irondeck-idioma",l)}catch(e){}}
var g=null;try{g=localStorage.getItem("irondeck-idioma")}catch(e){}poner(g==="en"?"en":"es");
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[hreflang]");if(!a)return;e.preventDefault();poner(a.getAttribute("hreflang"));window.scrollTo(0,0)});})();</script>"""


def fragmento(sitio, novedades, css):
    """Vista previa de claude.ai: sin <html>/<head>, con los dos idiomas y el cambio en la misma página
    (la vista previa no siempre deja pasar de un archivo a otro)."""
    return (f"<title>IronDeck</title>\n<link rel=\"stylesheet\" href=\"{GOOGLE_FONTS}\">\n"
            f"<style>\n{css}\n</style>\n{CAMBIO_IDIOMA}\n{cuerpo(None, sitio, novedades, '#idioma')}\n")


def sitemap(sitio, novedades):
    base = sitio["base"]
    # lastmod real: la portada cambia con cada novedad; las páginas legales, con su vigencia
    fechas = [str(n["fecha"]) for n in novedades if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(n["fecha"]))]
    portada = max(fechas) if fechas else datetime.date.today().isoformat()
    grupos = [(base, base + "en/", portada)]
    if sitio["_legal"]["listo"]:
        grupos += [(base + LEGALES[c]["es"][0], base + "en/" + LEGALES[c]["en"][0], sitio["_legal"]["vigencia"])
                   for c in LEGALES]
    urls = ""
    for es, en, fecha in grupos:
        alternos = (f'    <xhtml:link rel="alternate" hreflang="es" href="{es}"/>\n'
                    f'    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>\n'
                    f'    <xhtml:link rel="alternate" hreflang="x-default" href="{en}"/>\n')
        urls += "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{fecha}</lastmod>\n{alternos}  </url>\n"
                        for u in (es, en))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")


def escribir(ruta, texto):
    """Escribe con fin de línea LF también en Windows."""
    with open(ruta, "w", encoding="utf-8", newline="\n") as archivo:
        archivo.write(texto)


def main():
    sitio = json.loads((RAIZ / "sitio.json").read_text(encoding="utf-8"))
    novedades = json.loads((RAIZ / "novedades.json").read_text(encoding="utf-8"))["novedades"]
    css = (RAIZ / "fuente" / "estilos.css").read_text(encoding="utf-8")
    for clave, valor in sitio["enlaces"].items():
        if valor and not valor.startswith("https://"):
            sys.exit(f"El enlace «{clave}» tiene que empezar por https://")
    token = sitio.get("analiticaCloudflare", "")
    if token and not re.fullmatch(r"[A-Za-z0-9]+", token):
        sys.exit("El token de analiticaCloudflare solo lleva letras y números")
    sitio = con_legal(sitio)
    legal = sitio["_legal"]

    escribir(RAIZ / "index.html", pagina_completa("es", sitio, novedades, css))
    (RAIZ / "en").mkdir(exist_ok=True)
    escribir(RAIZ / "en" / "index.html", pagina_completa("en", sitio, novedades, css))
    for clave in LEGALES:
        for idioma, ruta in (("es", RAIZ / LEGALES[clave]["es"][0]), ("en", RAIZ / "en" / LEGALES[clave]["en"][0])):
            if legal["listo"]:
                escribir(ruta, pagina_legal(clave, idioma, sitio, css))
            elif ruta.exists():
                ruta.unlink()  # una página legal publicada antes no puede quedar con datos viejos
    escribir(RAIZ / "sitemap.xml", sitemap(sitio, novedades))
    if legal["listo"]:
        print("Listo: index.html, en/index.html, las 6 páginas legales y sitemap.xml")
    else:
        print("Listo: index.html, en/index.html y sitemap.xml")
        faltan = [n for n in ("titular", "correo", "vigencia") if not legal[n]]
        if faltan:
            print(f"Aviso: falta {', '.join(faltan)} en sitio.json → legal. Las páginas legales no se publican todavía.")
        if legal["futura"]:
            print(f"Aviso: la vigencia {legal['vigencia']} es futura. Las páginas legales se publican al armar desde ese día.")
        if legal["apagados"]:
            print(f"Aviso: quedan apagados hasta entonces: {', '.join(legal['apagados'])}.")

    if "--vista-previa" in sys.argv:
        destino = pathlib.Path(sys.argv[sys.argv.index("--vista-previa") + 1])
        destino.mkdir(parents=True, exist_ok=True)
        escribir(destino / "irondeck.html", fragmento(sitio, novedades, css))
        escribir(destino / "legal.html", fragmento_legal(sitio, css))
        print(f"Vistas previas en {destino}")


if __name__ == "__main__":
    main()
