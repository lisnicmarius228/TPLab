# Laborator: funcții, metode și importuri pe web
# Student: <numele vostru>
"""webtools: funcții reutilizabile pentru analiza unui site web."""

import csv
import json
import re
import socket
import ssl
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde
STUDENT = "NumePrenume"  # înlocuiește cu numele tău, fără diacritice și fără spații

# Ex. 47: constantă de modul, folosită în fetch()
DEFAULT_HEADERS = {"User-Agent": "WebLab-" + STUDENT}

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


def fetch(url: str, timeout: int = TIMEOUT) -> requests.Response:
    """Descarcă url cu antetele implicite și returnează obiectul răspuns."""
    return requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)


def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa url."""
    return fetch(url).status_code


def get_title(html: str) -> str:
    """Returnează textul dintre <title> și </title>, sau un șir gol dacă lipsește."""
    start = html.find("<title>")
    end = html.find("</title>")
    if start == -1 or end == -1:
        return ""
    return html[start + len("<title>"):end].strip()


def security_headers(url: str) -> dict:
    """Returnează {antet: True/False} pentru cele cinci antete de securitate."""
    response = fetch(url)
    return {header: header in response.headers for header in SECURITY_HEADERS}


def score_headers(results: dict) -> str:
    """Transformă dicționarul din security_headers într-un scor, ex. '3/5'."""
    return f"{sum(results.values())}/{len(results)}"


def check_paths(base: str, paths: list) -> dict:
    """Returnează {cale: cod_de_stare} pentru fiecare cale din listă."""
    results = {}
    for path in paths:
        try:
            results[path] = fetch(base + path).status_code
        except requests.RequestException:
            results[path] = None
        time.sleep(1)
    return results


def extract_links(html: str) -> list:
    """Returnează legăturile href din html, fără duplicate (păstrând ordinea)."""
    return list(dict.fromkeys(re.findall(r'href="([^"]+)"', html)))


def split_links(links: list, domain: str, base: str = BASE_URL):
    """Împarte legăturile în (interne, externe) față de domeniul dat."""
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


def fetch_robots(base: str):
    """Returnează textul fișierului /robots.txt sau None dacă fișierul lipsește."""
    try:
        response = fetch(base + "/robots.txt")
    except requests.RequestException:
        return None
    return response.text if response.status_code == 200 else None


def disallowed_paths(robots_text) -> list:
    """Returnează lista valorilor Disallow: din robots.txt (listă goală pentru None)."""
    if not robots_text:
        return []
    paths = []
    for line in robots_text.splitlines():
        line = line.split("#")[0].strip()
        if line.lower().startswith("disallow:"):
            value = line.split(":", 1)[1].strip()
            if value:
                paths.append(value)
    return paths


def resolve(hostname: str) -> str:
    """Returnează adresa IP (IPv4) a domeniului hostname."""
    return socket.gethostbyname(hostname)


def cert_days_left(hostname: str) -> int:
    """Returnează câte zile mai sunt până la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            cert = secure_sock.getpeercert()
    expires_at = ssl.cert_time_to_seconds(cert["notAfter"])
    return int((expires_at - time.time()) // 86400)


def redirect_chain(host: str) -> list:
    """Returnează lanțul de redirecționări pornind de la http://host, ca listă de texte."""
    response = fetch("http://" + host)
    chain = []
    for index, step in enumerate(response.history):
        next_url = (
            response.history[index + 1].url if index + 1 < len(response.history)
            else response.url
        )
        chain.append(f"{step.status_code} -> {next_url}")
    return chain


def save_csv(results: dict, filename: str = "report.csv") -> None:
    """Ex. 49: salvează {cale: status} în CSV, cu coloanele path, status, checked_at."""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["path", "status", "checked_at"])
        for path, status in results.items():
            writer.writerow([path, status, datetime.now().isoformat()])


def site_report(url: str, filename: str = "report.json") -> dict:
    """Ex. 50: colectează informații despre site, le afișează și le salvează în JSON."""
    parsed = urlparse(url)
    host = parsed.netloc

    response = fetch(url)
    time.sleep(1)

    try:
        ip = resolve(host)
    except OSError:
        ip = None

    try:
        chain = redirect_chain(host)
    except requests.RequestException:
        chain = []
    time.sleep(1)

    score = score_headers(security_headers(url))
    time.sleep(1)

    days_left = None
    if parsed.scheme == "https":
        try:
            days_left = cert_days_left(host)
        except (OSError, ssl.SSLError):
            days_left = None

    internal, external = split_links(extract_links(response.text), host, base=url)
    time.sleep(1)
    disallowed = disallowed_paths(fetch_robots(f"{parsed.scheme}://{host}"))

    report = {
        "url": url,
        "status_code": response.status_code,
        "final_url": response.url,
        "title": get_title(response.text),
        "ip": ip,
        "redirects": chain,
        "security_score": score,
        "cert_days_left": days_left,
        "internal_links": len(internal),
        "external_links": len(external),
        "disallowed_paths": disallowed,
    }

    print(f"=== Raport site: {url} ===")
    print(f"Cod de stare:      {report['status_code']}  (URL final: {report['final_url']})")
    print(f"Titlu:             {report['title']}")
    print(f"Adresă IP:         {report['ip']}")
    print(f"Redirecționări:    {', '.join(chain) if chain else 'niciuna'}")
    print(f"Scor securitate:   {report['security_score']}")
    cert_text = f"{days_left} de zile rămase" if days_left is not None else "indisponibil"
    print(f"Certificat:        {cert_text}")
    print(f"Legături:          {len(internal)} interne, {len(external)} externe")
    print(f"Căi interzise:     {', '.join(disallowed) if disallowed else 'niciuna'}")

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    print(f"Salvat în {filename}")
    return report


# Ex. 46: acest bloc rulează doar când fișierul este pornit direct
# (python webtools.py), nu și când este importat (import webtools).
if __name__ == "__main__":
    print("Autotest:", get_status("https://cybercor.org"))
