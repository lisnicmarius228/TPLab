# Laborator: funcții, metode și importuri pe web
# Student: <Lisnic Marius>

import argparse
from urllib.parse import urlparse

import webtools  # Ex. 44: importăm întregul modul
from webtools import DEFAULT_HEADERS, check_paths, get_title, save_csv, security_headers, site_report  # Ex. 45, 47

# Ex. 45: dacă main.py ar avea și o funcție proprie numită get_title, definiția din
# main.py ar înlocui (ar "umbri") get_title importată din webtools, deoarece ultimul
# nume definit în fișier este cel folosit. Din acest motiv e mai sigur să folosim
# webtools.get_title(...), care nu se poate suprapune cu numele din main.py.

# Ex. 46: blocul if __name__ == "__main__" din webtools.py rulează doar când pornim
# direct python webtools.py (atunci __name__ este "__main__"). Când main.py face
# import webtools, __name__ în webtools este "webtools", deci autotestul nu rulează.


def main() -> None:
    """Citește URL-ul din linia de comandă și generează raportul site-ului."""
    # Ex. 48: argumente din linia de comandă
    parser = argparse.ArgumentParser(description="Raport despre un site web")
    parser.add_argument("url", nargs="?", default=webtools.BASE_URL,
                        help="adresa site-ului, ex.: https://cybercor.org")
    args = parser.parse_args()
    url = args.url

    # Ex. 44: folosim modulul nostru
    print("Titlu:", webtools.get_title(webtools.fetch(url).text))

    # Ex. 45: nume importate direct (get_title, security_headers)
    print("Scor antete:", webtools.score_headers(security_headers(url)))

    # Ex. 47: constanta importată
    print("DEFAULT_HEADERS:", DEFAULT_HEADERS)
    print()

    # Ex. 49: raport CSV
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    results = check_paths(base, ["/", "/robots.txt", "/sitemap.xml"])
    save_csv(results, "report.csv")
    print("Salvat în report.csv\n")

    # Ex. 50: proiectul final
    site_report(url)


if __name__ == "__main__":
    main()
