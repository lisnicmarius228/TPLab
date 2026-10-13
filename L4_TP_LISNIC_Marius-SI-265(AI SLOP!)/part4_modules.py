# Laborator: funcții, metode și importuri pe web
# Student: <Lisnic Marius>

import hashlib
import json
import re
import socket
import ssl
import time
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# --- Ex. 35: descompunerea unui URL ---
print("Ex. 35")
parts = urlparse("https://cybercor.org/path?x=1#top")
print("scheme:  ", parts.scheme)
print("netloc:  ", parts.netloc)
print("path:    ", parts.path)
print("query:   ", parts.query)
print("fragment:", parts.fragment)

# --- Ex. 36: compunerea URL-urilor ---
print("\nEx. 36")
for link in ["/about", "contact.html", "../index.html"]:
    print(link, "->", urljoin(BASE_URL, link))


# --- Ex. 37: extragerea legăturilor ---
def extract_links(html: str) -> list:
    """Returnează toate legăturile href din html, fără duplicate (păstrând ordinea)."""
    links = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(links))


# --- Ex. 38: interne sau externe? ---
def split_links(links: list, domain: str, base: str = BASE_URL):
    """Împarte legăturile în (interne, externe) față de domeniul dat.

    Legăturile relative sunt transformate mai întâi în adrese complete cu urljoin.
    Legăturile care nu sunt http/https (mailto:, javascript: etc.) sunt ignorate.
    """
    internal, external = [], []
    for link in links:
        full = urljoin(base, link)
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc == domain:
            internal.append(full)
        else:
            external.append(full)
    return internal, external


# --- Ex. 39: propriile metode (HTMLParser) ---
class ImageFinder(HTMLParser):
    """Colectează atributul src al fiecărui tag <img> dintr-un document HTML."""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        """Apelată automat de HTMLParser pentru fiecare tag de deschidere."""
        if tag == "img":  # HTMLParser transformă numele tag-urilor în litere mici
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)


test_html = """
<html><body>
  <img src="/logo.png" alt="Logo">
  <IMG SRC="poza.jpg">
  <img alt="imagine fără src">
  <img src="https://cdn.example.com/banner.webp" />
  <a href="/despre">Aceasta nu este o imagine</a>
</body></html>
"""

finder = ImageFinder()
finder.feed(test_html)
print("\nEx. 39 (test):", finder.images)

assert finder.images == [
    "/logo.png",                            # imagine obișnuită
    "poza.jpg",                             # tag scris cu majuscule
    "https://cdn.example.com/banner.webp",  # tag care se închide singur
], "Parserul nu a găsit exact imaginile așteptate"
print("Testul a trecut!")

response = requests.get(BASE_URL, timeout=TIMEOUT)
finder = ImageFinder()
finder.feed(response.text)
print(len(finder.images), "imagini găsite")
for src in finder.images:
    print(src)
print("Număr de '<img' în text:", response.text.lower().count("<img"))
time.sleep(1)


# --- Ex. 40: amprenta paginii ---
def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 (hex) a conținutului paginii de la url."""
    response = requests.get(url, timeout=TIMEOUT)
    return hashlib.sha256(response.content).hexdigest()


print("\nEx. 40")
first = page_fingerprint(BASE_URL)
time.sleep(1)
second = page_fingerprint(BASE_URL)
print(first)
print(second)
print("Identice:", first == second)
# Amprentele ar fi diferite dacă pagina s-a schimbat între cele două cereri (text
# nou, dată sau oră afișată, token/nonce generat la fiecare cerere, reclame etc.).
# Chiar și un singur caracter modificat schimbă complet amprenta.
time.sleep(1)

# --- Ex. 41: salvarea în JSON ---
print("\nEx. 41")
with open("headers.json", "w", encoding="utf-8") as file:
    json.dump(dict(response.headers), file, indent=2)
with open("headers.json", encoding="utf-8") as file:
    loaded = json.load(file)
print("Content-Type din fișier:", loaded.get("Content-Type"))


# --- Ex. 42: interogare DNS ---
def resolve(hostname: str) -> str:
    """Returnează adresa IP (IPv4) a domeniului hostname."""
    return socket.gethostbyname(hostname)


print("\nEx. 42: cybercor.org ->", resolve("cybercor.org"))


# --- Ex. 43: expirarea certificatului ---
def cert_days_left(hostname: str) -> int:
    """Returnează câte zile mai sunt până la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            cert = secure_sock.getpeercert()
    expires_at = ssl.cert_time_to_seconds(cert["notAfter"])
    return int((expires_at - time.time()) // 86400)


print("\nEx. 43:", cert_days_left("cybercor.org"), "zile rămase")

# --- Verificați-vă ---
# handle_starttag() este apelată de HTMLParser însuși: când apelăm feed(), parserul
# citește textul HTML și, de fiecare dată când întâlnește un tag de deschidere,
# apelează automat metoda noastră. Acesta este un mecanism de tip "callback".
