# Laborator: funcții, metode și importuri pe web
# Student: <Lisnic Marius>

import time

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde
STUDENT = "NumePrenume"  # înlocuiește cu numele tău, fără diacritice și fără spații

# --- Ex. 1: primul import ---
import requests
print("Versiune requests:", requests.__version__)
import urllib.request
import urllib.error
# requests este o bibliotecă externă (nu vine cu Python), de aceea are nevoie de
# pip install. urllib face parte din biblioteca standard, deci e deja instalată
# odată cu Python.

# --- Ex. 2: două stiluri de import ---
response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Ex. 2 (import requests):", response.status_code)
time.sleep(1)

from requests import get
response = get(BASE_URL, timeout=TIMEOUT)
print("Ex. 2 (from requests import get):", response.status_code)
# import requests: se vede clar de unde vine funcția (requests.get), fără
#   riscul de a încurca numele cu alte funcții.
# from requests import get: codul e mai scurt, nu repeți numele modulului.
time.sleep(1)

# --- Ex. 3: alias-uri ---
import requests as rq
response = rq.get(BASE_URL, timeout=TIMEOUT)
print("Ex. 3:", response.status_code)
# Un alias face codul mai ușor de citit când numele modulului e lung și se
#   repetă des, iar alias-ul e unul cunoscut (ex.: import numpy as np).
# Îl face mai greu de citit când alias-ul e ales arbitrar (ex.: import requests
#   as x), pentru că nu mai știi de unde vine funcția.
time.sleep(1)

# --- Ex. 4: doar biblioteca standard ---
# urllib se prezintă implicit ca "Python-urllib", iar serverul îl refuză (403).
# De aceea setăm un User-Agent propriu printr-un obiect Request.
req = urllib.request.Request(BASE_URL, headers={"User-Agent": "WebLab-" + STUDENT})
try:
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        print("Ex. 4 status:", resp.status)
        body = resp.read().decode("utf-8")  # .read() dă bytes; .decode() dă str
        print(body[:200])
except urllib.error.HTTPError as e:
    print("Ex. 4: serverul a răspuns cu eroarea", e.code)
time.sleep(1)

# --- Ex. 5: priviți în interiorul unui modul ---
print(dir(requests))
# get        -> funcție
# Session    -> clasă
# exceptions -> modul

# --- Ex. 6: citiți documentația ---
help(requests.get)
# Parametrul care setează timpul maxim de așteptare este timeout.
response = requests.get(BASE_URL, timeout=5)
print("Ex. 6:", response.status_code)
time.sleep(1)

# --- Ex. 7: cronometrarea unei cereri ---
start = time.perf_counter()
response = requests.get(BASE_URL, timeout=TIMEOUT)
end = time.perf_counter()
print(f"Ex. 7 perf_counter:     {end - start:.3f} s")
print(f"Ex. 7 response.elapsed: {response.elapsed.total_seconds():.3f} s")
# perf_counter măsoară tot timpul scurs în cod, inclusiv citirea corpului.
# response.elapsed măsoară doar de la trimiterea cererii până la sosirea
# antetelor răspunsului, deci de obicei e puțin mai mic.

# --- Ex. 8: când un import eșuează ---
try:
    import bs4
    print("Ex. 8: bs4 este instalat")
except ImportError:
    print("Instalați modulul cu: pip install beautifulsoup4")

# --- Verificați-vă ---
# Modul   = un singur fișier .py care conține cod reutilizabil.
# Pachet  = un director cu mai multe module (are un fișier __init__.py).
# Bibliotecă = termen general pentru o colecție de cod reutilizabil; poate fi
#              un modul sau un pachet (ex.: requests este o bibliotecă).
