# Laborator: funcții, metode și importuri pe web
# Student: <Lisnic Marius>

import time
import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# --- Ex. 21 + Ex. 23: fetch cu parametru implicit ---
def fetch(url: str, timeout: int = 10) -> requests.Response:
    """Descarcă url și returnează obiectul răspuns (timeout implicit: 10 secunde)."""
    return requests.get(url, timeout=timeout)


print("Ex. 21:", fetch(BASE_URL).status_code)
time.sleep(1)
print("Ex. 23 (implicit):", fetch(BASE_URL).status_code)
time.sleep(1)
print("Ex. 23 (timeout=3):", fetch(BASE_URL, timeout=3).status_code)
time.sleep(1)


# --- Ex. 22 + Ex. 26: get_status cu type hints ---
def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa url."""
    response = requests.get(url, timeout=TIMEOUT)
    return response.status_code


print("\nEx. 22")
for path in ["/", "/robots.txt", "/sitemap.xml"]:
    print(path, "->", get_status(BASE_URL + path))
    time.sleep(1)

print("\nEx. 26")
try:
    get_status(123)
except Exception as e:
    print("Eroare:", type(e).__name__, "-", e)
# Adnotările de tip NU opresc programul: Python nu le verifică la rulare, sunt doar
# indicii pentru programatori și pentru editoare. Eroarea apare abia când requests
# încearcă să folosească valoarea 123 ca URL.


# --- Ex. 24 + Ex. 25: get_title cu docstring ---
def get_title(html: str) -> str:
    """Returnează textul dintre <title> și </title> dintr-un șir HTML.

    Parametri:
        html: codul HTML al paginii (șir de caractere).
    Returnează:
        titlul curățat de spații, sau un șir gol dacă nu există titlu.
    Funcția nu face operații de rețea.
    """
    start = html.find("<title>")
    end = html.find("</title>")
    if start == -1 or end == -1:
        return ""
    start += len("<title>")
    return html[start:end].strip()


print("\nEx. 24:", get_title(fetch(BASE_URL).text))
print("\nEx. 25:")
help(get_title)
time.sleep(1)


# --- Ex. 27: page_exists ---
def page_exists(url: str) -> bool:
    """Returnează True dacă pagina răspunde cu succes, altfel False (fără erori)."""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        return response.ok
    except requests.RequestException:
        return False


print("\nEx. 27")
print(page_exists(BASE_URL))
time.sleep(1)
print(page_exists("https://this-domain-does-not-exist.invalid"))
time.sleep(1)


# --- Ex. 28: check_paths ---
def check_paths(base: str, paths: list) -> dict:
    """Returnează un dicționar {cale: cod_de_stare} pentru fiecare cale din listă."""
    results = {}
    for path in paths:
        try:
            results[path] = requests.get(base + path, timeout=TIMEOUT).status_code
        except requests.RequestException:
            results[path] = None
        time.sleep(1)
    return results


print("\nEx. 28:", check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"]))


# --- Ex. 29: get_header cu argumente cu nume ---
def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returnează valoarea antetului name de la url, sau default dacă lipsește."""
    response = requests.get(url, timeout=TIMEOUT)
    return response.headers.get(name, default)


print("\nEx. 29:", get_header(BASE_URL, name="Server"))
time.sleep(1)

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


# --- Ex. 30: security_headers ---
def security_headers(url: str) -> dict:
    """Returnează {antet: True/False} pentru cele cinci antete de securitate."""
    response = requests.get(url, timeout=TIMEOUT)
    return {header: header in response.headers for header in SECURITY_HEADERS}


# --- Ex. 31: score_headers ---
def score_headers(results: dict) -> str:
    """Primește dicționarul din security_headers și returnează un scor, ex. '3/5'."""
    return f"{sum(results.values())}/{len(results)}"


print("\nEx. 30:", security_headers(BASE_URL))
time.sleep(1)
print("Ex. 31:", score_headers(security_headers(BASE_URL)))
time.sleep(1)


# --- Ex. 32: fetch_robots + disallowed_paths ---
def fetch_robots(base: str):
    """Returnează textul fișierului /robots.txt sau None dacă fișierul lipsește."""
    try:
        response = requests.get(base + "/robots.txt", timeout=TIMEOUT)
    except requests.RequestException:
        return None
    return response.text if response.status_code == 200 else None


def disallowed_paths(robots_text) -> list:
    """Returnează lista valorilor Disallow: din robots.txt (listă goală pentru None)."""
    if not robots_text:
        return []
    paths = []
    for line in robots_text.splitlines():
        line = line.split("#")[0].strip()  # ignorăm comentariile
        if line.lower().startswith("disallow:"):
            value = line.split(":", 1)[1].strip()
            if value:
                paths.append(value)
    return paths


print("\nEx. 32:", disallowed_paths(fetch_robots(BASE_URL)))
print("Ex. 32 (None):", disallowed_paths(None))
time.sleep(1)


# --- Ex. 33: response_times cu *args ---
def response_times(*urls: str) -> dict:
    """Returnează {url: secunde} pentru oricâte adrese primește."""
    times = {}
    for url in urls:
        start = time.perf_counter()
        requests.get(url, timeout=TIMEOUT)
        times[url] = round(time.perf_counter() - start, 3)
        time.sleep(1)
    return times


print("\nEx. 33:", response_times(BASE_URL, BASE_URL + "/robots.txt"))


# --- Ex. 34: log cu **kwargs ---
def log(message: str, **details) -> None:
    """Afișează mesajul urmat de fiecare detaliu, în forma: mesaj | cheie=valoare."""
    parts = [message] + [f"{key}={value}" for key, value in details.items()]
    print(" | ".join(parts))


print("\nEx. 34")
log("verificat", url=BASE_URL, status=200)

# --- Verificați-vă ---
# print() doar afișează o valoare pe ecran; după aceea valoarea se pierde și funcția
# returnează None. return trimite valoarea înapoi către cel care a apelat funcția,
# care o poate salva într-o variabilă, o poate folosi în calcule sau o poate da altei
# funcții (ca în score_headers(security_headers(...))).
