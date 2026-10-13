# Laborator: funcții, metode și importuri pe web
# Student: <numele vostru>

import time
import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde
STUDENT = "NumePrenume"  # înlocuiește cu numele tău, fără diacritice și fără spații

response = requests.get(BASE_URL, timeout=TIMEOUT)
time.sleep(1)

# --- Ex. 9: elementele de bază ale răspunsului ---
print("Ex. 9")
print(response.status_code)  # atribut
print(response.ok)           # atribut
print(response.url)          # atribut
print(response.encoding)     # atribut
# Toate sunt atribute (valori, fără paranteze). Metodele se apelează cu paranteze,
# de exemplu response.json() sau response.raise_for_status().

# --- Ex. 10: tratarea erorilor cu o metodă ---
print("\nEx. 10")
response.raise_for_status()  # pe pagina principală nu face nimic (cod 200)
print("Pagina principală este OK")
time.sleep(1)
try:
    bad = requests.get(BASE_URL + "/this-page-does-not-exist", timeout=TIMEOUT)
    bad.raise_for_status()
except requests.HTTPError as e:
    print("Pagina cerută nu există sau serverul a răspuns cu eroare:", e)
time.sleep(1)

# --- Ex. 11: toate antetele ---
print("\nEx. 11")
for name, value in response.headers.items():
    print(f"{name}: {value}")

# --- Ex. 12: metode de dicționar ---
print("\nEx. 12")
print("Server:", response.headers.get("Server", "lipsește"))
print("Content-Type:", response.headers.get("Content-Type", "lipsește"))
print("content-type (litere mici):", response.headers.get("content-type", "lipsește"))
# Observație: se obține aceeași valoare, deoarece response.headers nu este un
# dicționar obișnuit, ci unul care ignoră diferența dintre litere mari și mici
# (CaseInsensitiveDict), așa cum cere standardul HTTP pentru numele antetelor.

# --- Ex. 13: înlănțuirea metodelor de șir ---
print("\nEx. 13")
count = response.text.lower().count("cyber")
print("Cuvântul 'cyber' apare de", count, "ori")
# Putem înlănțui .lower() și .count() deoarece .lower() returnează un șir nou (str),
# iar pe acel șir se poate apela direct o altă metodă de șir, adică .count().

# --- Ex. 14: găsirea titlului ---
print("\nEx. 14")
html = response.text
start = html.find("<title>")
end = html.find("</title>")
if start != -1 and end != -1:
    start += len("<title>")
    print("Titlu:", html[start:end].strip())
else:
    print("Pagina nu are tag <title>")

# --- Ex. 15: numărarea liniilor ---
print("\nEx. 15")
lines = html.splitlines()
print("Număr de linii:", len(lines))
if lines:
    print("Lungimea celei mai lungi linii:", len(max(lines, key=len)))

# --- Ex. 16: verificarea HTTPS ---
print("\nEx. 16")
if response.url.startswith("https://"):
    print("Conexiune securizată")
else:
    print("Conexiune nesecurizată")

# --- Ex. 17: urmărirea redirecționărilor ---
print("\nEx. 17")
time.sleep(1)
r = requests.get("http://cybercor.org", timeout=TIMEOUT)
for step in r.history:
    print(step.status_code, step.url)
print("URL final:", r.url)
time.sleep(1)

# --- Ex. 18: HEAD versus GET ---
print("\nEx. 18")
head = requests.head(BASE_URL, timeout=TIMEOUT)
time.sleep(1)
get_ = requests.get(BASE_URL, timeout=TIMEOUT)
print("HEAD:", len(head.content), "octeți")
print("GET: ", len(get_.content), "octeți")
# HEAD cere doar antetele, nu și corpul paginii, de aceea content are lungimea 0.
# GET returnează și antetele, și corpul (codul HTML complet).
time.sleep(1)

# --- Ex. 19: cookie-uri ---
print("\nEx. 19")
if len(response.cookies) == 0:
    print("Niciun cookie setat")
else:
    for cookie in response.cookies:
        print(cookie.name, cookie.secure)

# --- Ex. 20: sesiuni ---
print("\nEx. 20")
session = requests.Session()
session.headers.update({"User-Agent": "WebLab-" + STUDENT})
echo = session.get(ECHO_URL + "/headers", timeout=TIMEOUT)
print(echo.json())
print("User-Agent primit de server:", echo.json()["headers"].get("User-Agent"))

# --- Verificați-vă ---
# response.text este un atribut (o valoare deja calculată), deci se citește fără
# paranteze. response.json() este o metodă: face o acțiune (transformă textul în
# dicționar/listă Python), iar acțiunile se apelează cu paranteze.
