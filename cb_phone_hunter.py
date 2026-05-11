#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
#   CB-PHONEHUNTER v1.0 — Ciberbrigada OSINT Suite
#   Reconocimiento OSINT de números telefónicos en fuentes abiertas
#   Uso exclusivo para fines legales y educativos
# ═══════════════════════════════════════════════════════════════════════════════

import sys
import time
import os
import re
import json
import urllib.parse
import hashlib

try:
    import requests
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    os.system("pip install requests colorama phonenumbers --break-system-packages -q")
    import requests
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
    from colorama import init, Fore, Style
    init(autoreset=True)

# ── Colores ───────────────────────────────────────────────────────────────────
C  = Fore.CYAN
Y  = Fore.YELLOW
G  = Fore.GREEN
R  = Fore.RED
W  = Fore.WHITE
D  = Fore.WHITE + Style.DIM
M  = Fore.MAGENTA
B  = Style.BRIGHT
RS = Style.RESET_ALL

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# ══════════════════════════════════════════════════════════════════════════════
# BANNER
# ══════════════════════════════════════════════════════════════════════════════
def banner():
    os.system("cls" if os.name == "nt" else "clear")

    CYAN = '\033[96m'
    ORAN = '\033[38;5;208m'
    DIM  = '\033[2m\033[37m'
    BOLD = '\033[1m'
    YEL  = '\033[33m'
    RST  = '\033[0m'

    logo = [
        "              ...::::...               ",
        "              ..:::+: ....             ",
        "        .:...:::::::.  ..:....... ..   ",
        "       :+  .:::::::    ::::::::::.     ",
        "      .+. .::::::::    +::::::::++::   ",
        "    . ::.:+:.          :::       ::+:  ",
        "   .: :::+.            +:+       .+++  ",
        "   .+ .+::             +:+.    .:+++.  ",
        "    +: :+.             ++++++++++++:   ",
        "     +:.:+             +++:......:+++: ",
        "   :. :++++.           +++         ++%:",
        "    ::  .::+++:::::    +++        .++%:",
        "     .:::....::++++   .+++:.....::+++: ",
        "   ... ..:+::+::+++:. ::++++++++++:.   ",
        "     :+:. :+.:+:.:++::......  ...      ",
        "       :+: :+..++...::::.......         ",
        "         .. :+:..:+:.........           ",
    ]

    print()
    for line in logo:
        mid = len(line) // 2
        print(f"       {CYAN}{BOLD}{line[:mid]}{ORAN}{line[mid:]}{RST}")

    print(f"                          {DIM}by: Fgunther{RST}")
    print()
    print(f"  {CYAN}{BOLD}Ciber{ORAN}brigada{RST} {CYAN}OSINT Suite{RST}  {DIM}─────────────────────{RST}")
    print(f"  {BOLD}╔══════════════════════════════════════════╗{RST}")
    print(f"  {BOLD}║  📱  CB-PHONEHUNTER  v1.0               ║{RST}")
    print(f"  {BOLD}║  Phone OSINT — Fuentes abiertas         ║{RST}")
    print(f"  {BOLD}╚══════════════════════════════════════════╝{RST}")
    print(f"  {DIM}[ ciberbrigada.com ]  [ OSINT Suite ]{RST}")
    print(f"  {YEL}⚠  Solo para uso legal, ético y educativo  ⚠{RST}")
    print()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def separador(titulo=""):
    if titulo:
        pad = (56 - len(titulo)) // 2
        print(f"\n{C}{'─' * pad} {B}{titulo}{RS}{C} {'─' * pad}{RS}")
    else:
        print(f"{D}{'─' * 60}{RS}")

def ok(msg):   print(f"  {G}{B}[✓]{RS} {W}{msg}{RS}")
def warn(msg): print(f"  {Y}[!]{RS} {Y}{msg}{RS}")
def fail(msg): print(f"  {R}[✗]{RS} {D}{msg}{RS}")
def info(msg): print(f"  {C}[i]{RS} {W}{msg}{RS}")
def dato(k, v):print(f"  {C}  ▸ {D}{k}:{RS} {W}{B}{v}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1 — PHONENUMBERS (Info básica del número)
# ══════════════════════════════════════════════════════════════════════════════
def analizar_numero(phone_raw):
    separador("ANÁLISIS DEL NÚMERO")
    try:
        # Intentar parsear con y sin código de país
        try:
            parsed = phonenumbers.parse(phone_raw)
        except:
            parsed = phonenumbers.parse(phone_raw, "AR")  # Default Argentina

        es_valido   = phonenumbers.is_valid_number(parsed)
        es_posible  = phonenumbers.is_possible_number(parsed)

        # Formato internacional
        fmt_intl    = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        fmt_e164    = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        fmt_nacional= phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)

        dato("Número internacional", fmt_intl)
        dato("Formato E164",         fmt_e164)
        dato("Formato nacional",     fmt_nacional)
        dato("Válido",               f"{'✓ SÍ' if es_valido else '✗ NO'}")
        dato("Posible",              f"{'✓ SÍ' if es_posible else '✗ NO'}")

        # País
        pais = geocoder.description_for_number(parsed, "es")
        dato("País / Región",        pais or "Desconocido")

        # Operadora
        op = carrier.name_for_number(parsed, "es")
        dato("Operadora",            op or "No disponible")

        # Zona horaria
        zonas = list(timezone.time_zones_for_number(parsed))
        dato("Zona horaria",         ", ".join(zonas) if zonas else "No disponible")

        # Tipo de línea
        tipo = phonenumbers.number_type(parsed)
        tipos = {
            0: "FIJO",
            1: "MÓVIL",
            2: "FIJO O MÓVIL",
            3: "GRATUITO (0800)",
            4: "TARIFA PREMIUM",
            5: "COMPARTIDO",
            6: "VOIP",
            7: "PAGER",
            8: "UAN",
            9: "DESCONOCIDO",
            10: "EMERGENCIAS",
            27: "DESCONOCIDO",
        }
        dato("Tipo de línea",        tipos.get(tipo, "Desconocido"))

        # Código de país
        dato("Código de país",       f"+{parsed.country_code}")
        dato("Número nacional",      str(parsed.national_number))

        return fmt_e164, fmt_intl, parsed

    except Exception as e:
        fail(f"Error al analizar el número: {e}")
        warn("Asegurate de incluir el código de país (ej: +54 9 11 1234-5678)")
        return None, None, None

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2 — TRUECALLER (Nombre del dueño)
# ══════════════════════════════════════════════════════════════════════════════
def truecaller_check(fmt_e164):
    separador("TRUECALLER — Identificación")
    # Truecaller requiere auth token — usamos la web pública
    phone_clean = fmt_e164.replace("+", "").replace(" ", "")
    try:
        urls = [
            f"https://www.truecaller.com/search/ar/{phone_clean}",
            f"https://search.truecaller.com/search/{phone_clean}",
        ]
        for url in urls:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200 and len(r.text) > 500:
                body = r.text.lower()
                if "not found" not in body and "no results" not in body:
                    ok("Número encontrado en Truecaller")
                    dato("  URL", url)
                    # Extraer nombre si está en el HTML
                    match = re.search(r'"name"\s*:\s*"([^"]+)"', r.text)
                    if match:
                        dato("  Nombre", match.group(1))
                    return
        warn("No se encontró información en Truecaller")
        dato("  Buscar manualmente", f"https://www.truecaller.com/search/ar/{phone_clean}")
    except Exception as e:
        warn(f"Truecaller no disponible: {type(e).__name__}")
        dato("  Buscar manualmente", f"https://www.truecaller.com/search/ar/{phone_clean}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3 — WHATSAPP (¿Tiene cuenta?)
# ══════════════════════════════════════════════════════════════════════════════
def whatsapp_check(fmt_e164, fmt_intl):
    separador("WHATSAPP — Verificación")
    phone_clean = fmt_e164.replace("+", "").replace(" ", "")
    try:
        # WhatsApp API check (método wa.me)
        url = f"https://wa.me/{phone_clean}"
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)

        if r.status_code == 200:
            body = r.text.lower()
            if "send message" in body or "open whatsapp" in body or "whatsapp" in body:
                ok(f"Número activo en WhatsApp")
                dato("  Link directo", url)
                dato("  Abrir chat",   f"https://api.whatsapp.com/send?phone={phone_clean}")
            else:
                warn("No se pudo confirmar si tiene WhatsApp")
                dato("  Verificar", url)
        else:
            warn(f"WhatsApp respondió {r.status_code}")
            dato("  Verificar manualmente", url)
    except Exception as e:
        warn(f"No se pudo verificar WhatsApp: {type(e).__name__}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 4 — TELEGRAM (¿Tiene cuenta?)
# ══════════════════════════════════════════════════════════════════════════════
def telegram_check(fmt_e164):
    separador("TELEGRAM — Verificación")
    phone_clean = fmt_e164.replace("+", "").replace(" ", "")
    try:
        # Telegram no expone búsqueda pública por número
        # Mostramos links útiles
        info("Telegram no expone búsqueda pública por número de teléfono")
        dato("  Buscar en Telegram", f"tg://resolve?phone={phone_clean}")
        dato("  Link web",           f"https://t.me/+{phone_clean}")
        dato("  Buscar en TGStat",   f"https://tgstat.com/search?q={phone_clean}")
    except Exception as e:
        fail(f"Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 5 — EYECON / GETCONTACT (Nombres registrados)
# ══════════════════════════════════════════════════════════════════════════════
def getcontact_check(fmt_e164):
    separador("GETCONTACT — Nombres registrados")
    phone_clean = fmt_e164.replace("+", "")
    try:
        # GetContact API pública limitada
        r = requests.get(
            f"https://api.getcontact.com/v1/search/{phone_clean}",
            headers={**HEADERS, "Accept": "application/json"},
            timeout=10
        )
        if r.status_code == 200:
            d = r.json()
            tags = d.get("result", {}).get("tags", [])
            name = d.get("result", {}).get("name", "")
            if name:
                ok(f"Nombre encontrado: {name}")
            if tags:
                ok(f"Tags registrados: {', '.join(tags[:10])}")
            if not name and not tags:
                warn("Sin resultados en GetContact")
        else:
            warn(f"GetContact no disponible ({r.status_code})")
            dato("  Verificar manualmente", f"https://www.getcontact.com/en/search/{phone_clean}")
    except Exception as e:
        warn(f"GetContact no disponible: {type(e).__name__}")
        dato("  Verificar manualmente", f"https://www.getcontact.com/en/search/{phone_clean}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 6 — GOOGLE DORKS
# ══════════════════════════════════════════════════════════════════════════════
def google_dorks(fmt_intl, fmt_e164, phone_raw):
    separador("GOOGLE DORKS — Links de búsqueda")
    # Diferentes formatos del número
    phone_clean = fmt_e164.replace("+", "")
    phone_dots  = fmt_intl.replace(" ", ".")
    phone_dash  = fmt_intl.replace(" ", "-")

    dorks = [
        (f'"{fmt_intl}"',                                  "Número exacto internacional"),
        (f'"{phone_raw}"',                                  "Número como fue ingresado"),
        (f'"{phone_dots}" OR "{phone_dash}"',               "Formatos con punto/guión"),
        (f'"{fmt_intl}" site:linkedin.com',                 "LinkedIn"),
        (f'"{fmt_intl}" site:facebook.com',                 "Facebook"),
        (f'"{fmt_intl}" site:instagram.com',                "Instagram"),
        (f'"{fmt_intl}" nombre OR name OR owner',           "Nombre del dueño"),
        (f'"{fmt_intl}" email OR correo OR mail',           "Email asociado"),
        (f'intext:"{fmt_intl}" site:pastebin.com',          "Pastebin"),
        (f'"{fmt_intl}" whatsapp OR telegram OR signal',    "Mensajería"),
        (f'"{fmt_intl}" filetype:pdf',                      "En documentos PDF"),
        (f'"{phone_clean}" celular OR móvil OR teléfono',   "Menciones en español"),
    ]

    for dork, desc in dorks:
        encoded = urllib.parse.quote(dork)
        url = f"https://www.google.com/search?q={encoded}"
        print(f"  {C}▸ {W}{desc:<32}{RS} {D}{url[:65]}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 7 — REDES SOCIALES (Links directos)
# ══════════════════════════════════════════════════════════════════════════════
def social_links(fmt_e164):
    separador("REDES SOCIALES — Links de búsqueda")
    phone_clean = fmt_e164.replace("+", "").replace(" ", "")

    links = [
        ("WhatsApp",   f"https://wa.me/{phone_clean}"),
        ("Telegram",   f"https://t.me/+{phone_clean}"),
        ("Facebook",   f"https://www.facebook.com/search/top?q={urllib.parse.quote(fmt_e164)}"),
        ("Truecaller", f"https://www.truecaller.com/search/ar/{phone_clean}"),
        ("GetContact", f"https://www.getcontact.com/en/search/{phone_clean}"),
        ("Spy Dialer", f"https://spydialer.com/default.aspx?phone={phone_clean}"),
        ("CallerID",   f"https://www.calleridtest.com/phone-lookup/{phone_clean}"),
        ("NumLookup",  f"https://www.numlookup.com/?number={fmt_e164}"),
        ("ThatsThem",  f"https://thatsthem.com/phone/{phone_clean}"),
        ("Sync.me",    f"https://sync.me/search/?number={fmt_e164}"),
    ]

    for nombre, url in links:
        print(f"  {C}▸ {W}{nombre:<14}{RS} {D}{url}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 8 — GEOLOCALIZACIÓN (País, región, operadora)
# ══════════════════════════════════════════════════════════════════════════════
def geolocalizacion(fmt_e164):
    separador("GEOLOCALIZACIÓN — APIs públicas")
    phone_clean = fmt_e164.replace("+", "").replace(" ", "")
    try:
        # API gratuita de numverify (sin key, datos básicos)
        r = requests.get(
            f"https://phonevalidation.abstractapi.com/v1/?api_key=&phone={fmt_e164}",
            headers=HEADERS, timeout=8
        )
        if r.status_code == 200:
            d = r.json()
            dato("País",      d.get("country", {}).get("name", "—"))
            dato("Código",    d.get("country", {}).get("code", "—"))
            dato("Válido",    "SÍ" if d.get("valid") else "NO")
            dato("Tipo",      d.get("type", "—"))
            dato("Operadora", d.get("carrier", "—"))
    except Exception:
        pass

    # Fallback: ip-api para info del país
    try:
        # Extraer código de país del número
        from phonenumbers import geocoder as geo
        import phonenumbers as pn
        parsed = pn.parse(fmt_e164)
        region = pn.region_code_for_number(parsed)
        dato("Código de región", region or "—")
    except Exception:
        pass

    dato("Buscar en ip-api", f"https://ip-api.com/#phone/{phone_clean}")
    dato("NumLookup API",    f"https://www.numlookup.com/?number={fmt_e164}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 9 — RESUMEN FINAL
# ══════════════════════════════════════════════════════════════════════════════
def resumen(phone_raw, fmt_e164, fmt_intl):
    separador("RESUMEN")
    print(f"\n  {C}{B}Target:{RS}       {W}{B}{phone_raw}{RS}")
    print(f"  {C}{B}E164:{RS}         {W}{fmt_e164}{RS}")
    print(f"  {C}{B}Internacional:{RS} {W}{fmt_intl}{RS}")
    print(f"\n  {D}Análisis completado — Ciberbrigada OSINT Suite v1.0{RS}\n")

# ══════════════════════════════════════════════════════════════════════════════
# MENÚ DE MÓDULOS
# ══════════════════════════════════════════════════════════════════════════════
def menu_modulos():
    modulos = [
        ("1", "Análisis del número   — Formato, país, operadora, tipo"),
        ("2", "Truecaller            — Nombre del dueño"),
        ("3", "WhatsApp              — ¿Tiene cuenta activa?"),
        ("4", "Telegram              — Links de verificación"),
        ("5", "GetContact            — Nombres registrados"),
        ("6", "Google Dorks          — Links de búsqueda"),
        ("7", "Redes Sociales        — Links directos"),
        ("8", "Geolocalización       — País y operadora"),
        ("0", "TODOS LOS MÓDULOS"),
    ]
    separador("SELECCIONÁ LOS MÓDULOS")
    for num, desc in modulos:
        color = C if num != "0" else Y
        print(f"  {color}[{num}]{RS} {W}{desc}{RS}")
    print()
    try:
        sel = input(f"  {C}▸ Opción (ej: 0 o 1,3,5):{RS} ").strip()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

    if sel == "0":
        return ["1","2","3","4","5","6","7","8"]
    return [s.strip() for s in sel.split(",")]

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    banner()

    print(f"  {W}Ingresá el número a analizar con código de país{RS}")
    print(f"  {D}Ejemplos: +54 9 11 1234-5678 | +1 555 123 4567 | +34 612 345 678{RS}\n")

    while True:
        try:
            phone_raw = input(f"  {C}▸ Teléfono:{RS} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {Y}Saliendo... Hasta pronto.{RS}\n")
            sys.exit(0)

        if phone_raw.lower() in ("salir", "exit", "quit", "q"):
            print(f"\n  {Y}Saliendo... Hasta pronto.{RS}\n")
            sys.exit(0)

        if not phone_raw:
            warn("Ingresá un número de teléfono")
            continue

        # Analizar número primero
        fmt_e164, fmt_intl, parsed = analizar_numero(phone_raw)
        if not fmt_e164:
            continue

        # Menú de módulos
        selected = menu_modulos()
        print()

        if "2" in selected: truecaller_check(fmt_e164)
        if "3" in selected: whatsapp_check(fmt_e164, fmt_intl)
        if "4" in selected: telegram_check(fmt_e164)
        if "5" in selected: getcontact_check(fmt_e164)
        if "6" in selected: google_dorks(fmt_intl, fmt_e164, phone_raw)
        if "7" in selected: social_links(fmt_e164)
        if "8" in selected: geolocalizacion(fmt_e164)

        resumen(phone_raw, fmt_e164, fmt_intl)

        separador()
        print(f"\n  {D}¿Analizar otro número? (Enter para continuar / 'salir' para terminar){RS}")
        try:
            again = input(f"  {C}▸{RS} ").strip().lower()
            if again in ("salir", "exit", "quit", "q"):
                print(f"\n  {Y}Saliendo... Hasta pronto.{RS}\n")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {Y}Saliendo...{RS}\n")
            sys.exit(0)

        banner()

if __name__ == "__main__":
    main()
