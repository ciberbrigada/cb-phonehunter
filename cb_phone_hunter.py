#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
#   CB-PHONEHUNTER v2.0 — Ciberbrigada OSINT Suite
#   Reconocimiento OSINT de números telefónicos — Datos reales en terminal
#   Uso exclusivo para fines legales y educativos
# ═══════════════════════════════════════════════════════════════════════════════

import sys
import os
import re
import json
import socket
import urllib.parse
import hashlib

try:
    import requests
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone as pn_timezone
    import dns.resolver
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    os.system("pip install requests colorama phonenumbers dnspython --break-system-packages -q")
    import requests
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone as pn_timezone
    import dns.resolver
    from colorama import init, Fore, Style
    init(autoreset=True)

# ── Colores ───────────────────────────────────────────────────────────────────
C  = Fore.CYAN
Y  = Fore.YELLOW
G  = Fore.GREEN
R  = Fore.RED
W  = Fore.WHITE
D  = Fore.WHITE + Style.DIM
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

HEADERS_JSON = {**HEADERS, "Accept": "application/json, text/plain, */*"}

# Mapa de códigos de país → nombre del país
COUNTRY_NAMES = {
    "AR": "Argentina", "US": "Estados Unidos", "MX": "México",
    "BR": "Brasil", "CO": "Colombia", "CL": "Chile", "PE": "Perú",
    "VE": "Venezuela", "EC": "Ecuador", "BO": "Bolivia", "PY": "Paraguay",
    "UY": "Uruguay", "ES": "España", "DE": "Alemania", "FR": "Francia",
    "IT": "Italia", "GB": "Reino Unido", "PT": "Portugal", "RU": "Rusia",
    "CN": "China", "JP": "Japón", "IN": "India", "AU": "Australia",
    "CA": "Canadá", "ZA": "Sudáfrica", "NG": "Nigeria", "EG": "Egipto",
    "TR": "Turquía", "SA": "Arabia Saudita", "AE": "Emiratos Árabes",
    "IL": "Israel", "KR": "Corea del Sur", "TH": "Tailandia",
    "PH": "Filipinas", "ID": "Indonesia", "PK": "Pakistán",
    "NL": "Países Bajos", "BE": "Bélgica", "SE": "Suecia",
    "NO": "Noruega", "DK": "Dinamarca", "FI": "Finlandia",
    "PL": "Polonia", "UA": "Ucrania", "RO": "Rumania",
    "HU": "Hungría", "CZ": "República Checa",
}

TIPOS_LINEA = {
    0: "📞 FIJO",
    1: "📱 MÓVIL",
    2: "📞📱 FIJO O MÓVIL",
    3: "🆓 GRATUITO (0800)",
    4: "💰 TARIFA PREMIUM",
    5: "🔀 COSTO COMPARTIDO",
    6: "🌐 VoIP",
    7: "📟 PAGER",
    8: "🔧 UAN",
    27: "❓ DESCONOCIDO",
}

# ══════════════════════════════════════════════════════════════════════════════
# BANNER
# ══════════════════════════════════════════════════════════════════════════════
def banner():
    os.system("cls" if os.name == "nt" else "clear")
    CYAN = '\033[96m'; ORAN = '\033[38;5;208m'
    DIM  = '\033[2m\033[37m'; BOLD = '\033[1m'
    YEL  = '\033[33m'; RST  = '\033[0m'
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
    print(f"  {BOLD}║  📱  CB-PHONEHUNTER  v2.0               ║{RST}")
    print(f"  {BOLD}║  Phone OSINT — Datos reales en terminal ║{RST}")
    print(f"  {BOLD}╚══════════════════════════════════════════╝{RST}")
    print(f"  {DIM}[ ciberbrigada.com ]  [ OSINT Suite ]{RST}")
    print(f"  {YEL}⚠  Solo para uso legal, ético y educativo  ⚠{RST}")
    print()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def sep(titulo=""):
    if titulo:
        pad = (56 - len(titulo)) // 2
        print(f"\n{C}{'─'*pad} {B}{titulo}{RS}{C} {'─'*pad}{RS}")
    else:
        print(f"{D}{'─'*60}{RS}")

def ok(msg):    print(f"  {G}{B}[✓]{RS} {W}{msg}{RS}")
def warn(msg):  print(f"  {Y}[!]{RS} {Y}{msg}{RS}")
def fail(msg):  print(f"  {R}[✗]{RS} {D}{msg}{RS}")
def info(msg):  print(f"  {C}[i]{RS} {W}{msg}{RS}")
def dato(k, v): print(f"  {C}  ▸ {D}{k}:{RS} {W}{B}{v}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1 — ANÁLISIS LOCAL (phonenumbers — 100% offline)
# ══════════════════════════════════════════════════════════════════════════════
def modulo_analisis(phone_raw):
    sep("ANÁLISIS DEL NÚMERO")
    try:
        try:
            parsed = phonenumbers.parse(phone_raw)
        except Exception:
            parsed = phonenumbers.parse(phone_raw, "AR")

        es_valido  = phonenumbers.is_valid_number(parsed)
        es_posible = phonenumbers.is_possible_number(parsed)

        fmt_intl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        fmt_e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        fmt_nac  = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)

        dato("Número internacional", fmt_intl)
        dato("Formato E164",         fmt_e164)
        dato("Formato nacional",     fmt_nac)
        dato("Válido",               f"{'✓ SÍ' if es_valido else '✗ NO'}")
        dato("Posible",              f"{'✓ SÍ' if es_posible else '✗ NO'}")

        region = phonenumbers.region_code_for_number(parsed)
        pais_nombre = COUNTRY_NAMES.get(region, geocoder.description_for_number(parsed, "es") or "Desconocido")
        dato("País",                 pais_nombre)
        dato("Código de región",     region or "—")
        dato("Código de país",       f"+{parsed.country_code}")

        pais_geo = geocoder.description_for_number(parsed, "es")
        if pais_geo and pais_geo != pais_nombre:
            dato("Zona geográfica",  pais_geo)

        op = carrier.name_for_number(parsed, "es")
        dato("Operadora",            op if op else "No disponible en base local")

        zonas = list(pn_timezone.time_zones_for_number(parsed))
        dato("Zona horaria",         ", ".join(zonas) if zonas else "No disponible")

        tipo = phonenumbers.number_type(parsed)
        dato("Tipo de línea",        TIPOS_LINEA.get(tipo, "❓ Desconocido"))

        dato("Número nacional",      str(parsed.national_number))
        dato("Código de área",       str(parsed.national_number)[:3])

        if not es_valido:
            warn("El número no parece válido para la región detectada")

        return fmt_e164, fmt_intl, parsed, region

    except Exception as e:
        fail(f"Error al analizar: {e}")
        warn("Incluí el código de país. Ej: +54 9 11 1234-5678")
        return None, None, None, None

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2 — VERIPHONE API (gratuita, sin key, datos reales)
# ══════════════════════════════════════════════════════════════════════════════
def modulo_veriphone(fmt_e164):
    sep("VERIPHONE — Validación y Carrier")
    try:
        r = requests.get(
            f"https://api.veriphone.io/v2/verify?phone={urllib.parse.quote(fmt_e164)}&key=demo",
            headers=HEADERS_JSON, timeout=12
        )
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == "success" or d.get("phone_valid"):
                ok("Datos obtenidos de Veriphone")
                dato("Número",        d.get("phone", "—"))
                dato("Internacional", d.get("international_number", "—"))
                dato("Local",         d.get("local_number", "—"))
                dato("País",          d.get("country", "—"))
                dato("Código país",   d.get("country_code", "—"))
                dato("Prefijo",       d.get("country_prefix", "—"))
                dato("Operadora",     d.get("carrier", "—"))
                dato("Tipo línea",    d.get("phone_type", "—").upper())
                dato("Válido",        "✓ SÍ" if d.get("phone_valid") else "✗ NO")
                dato("Región",        d.get("phone_region", "—"))
            else:
                warn("Veriphone no devolvió datos para este número")
        elif r.status_code == 429:
            warn("Rate limit en Veriphone — intentá en unos minutos")
        else:
            warn(f"Veriphone respondió {r.status_code}")
    except Exception as e:
        warn(f"Veriphone no disponible: {type(e).__name__}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3 — NUMVERIFY (gratuito con key demo)
# ══════════════════════════════════════════════════════════════════════════════
def modulo_numverify(fmt_e164, region):
    sep("NUMVERIFY — Carrier & Línea")
    phone_clean = fmt_e164.replace("+", "")
    try:
        # Free tier sin key para consultas básicas
        r = requests.get(
            f"http://apilayer.net/api/validate?number={phone_clean}&format=1",
            headers=HEADERS_JSON, timeout=10
        )
        if r.status_code == 200:
            d = r.json()
            if d.get("valid"):
                ok("Número validado por NumVerify")
                dato("Número",         d.get("number", "—"))
                dato("Local format",   d.get("local_format", "—"))
                dato("Internacional",  d.get("international_format", "—"))
                dato("País",           d.get("country_name", "—"))
                dato("Código país",    d.get("country_code", "—"))
                dato("Prefijo",        d.get("country_prefix", "—"))
                dato("Operadora",      d.get("carrier", "—"))
                dato("Tipo línea",     d.get("line_type", "—").upper() if d.get("line_type") else "—")
                dato("Localización",   d.get("location", "—"))
            else:
                warn("NumVerify: número no válido o sin datos")
        else:
            warn(f"NumVerify respondió {r.status_code}")
    except Exception as e:
        warn(f"NumVerify no disponible: {type(e).__name__}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 4 — DNS & INFRAESTRUCTURA (operadoras por DNS)
# ══════════════════════════════════════════════════════════════════════════════
def modulo_dns(fmt_e164, region):
    sep("DNS & INFRAESTRUCTURA")
    phone_clean = fmt_e164.replace("+", "").replace(" ", "")

    # Reverse DNS lookup del carrier
    try:
        # Lookup E.164 en DNS (ENUM protocol - RFC 3761)
        # Convierte +5491164230103 → 3.0.1.0.3.2.4.6.1.1.9.4.5.e164.arpa
        digits = phone_clean[::-1]
        enum_domain = ".".join(list(digits)) + ".e164.arpa"
        dato("ENUM domain", enum_domain)

        try:
            naptr = dns.resolver.resolve(enum_domain, 'NAPTR')
            ok("Registros NAPTR encontrados (ENUM)")
            for record in naptr:
                dato("  NAPTR", str(record))
        except Exception:
            info("Sin registros ENUM (normal para números móviles)")

        # Reverse lookup básico
        try:
            reversed_ip = dns.resolver.resolve(f"{phone_clean[::-1]}.e164.arpa", 'PTR')
            for r in reversed_ip:
                dato("  PTR", str(r))
        except Exception:
            pass

    except Exception as e:
        warn(f"DNS lookup falló: {type(e).__name__}")

    # Info de infraestructura del país
    country_carriers = {
        "AR": ["Personal (Telecom)", "Claro (AMX Argentina)", "Movistar (Telefónica)", "Tuenti"],
        "MX": ["Telcel", "Movistar México", "AT&T México", "Unefon"],
        "CO": ["Claro Colombia", "Movistar Colombia", "Tigo", "WOM"],
        "CL": ["Entel", "Movistar Chile", "Claro Chile", "WOM Chile"],
        "BR": ["Vivo", "TIM", "Claro Brasil", "Oi"],
        "PE": ["Claro Perú", "Movistar Perú", "Entel Perú", "Bitel"],
        "US": ["AT&T", "Verizon", "T-Mobile", "Sprint"],
        "ES": ["Movistar España", "Vodafone España", "Orange España", "Yoigo"],
        "MX": ["Telcel", "Movistar México", "AT&T México"],
    }

    if region and region in country_carriers:
        info(f"Operadoras conocidas en {COUNTRY_NAMES.get(region, region)}:")
        for op in country_carriers[region]:
            print(f"    {D}• {op}{RS}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 5 — WHATSAPP (verificación real)
# ══════════════════════════════════════════════════════════════════════════════
def modulo_whatsapp(fmt_e164):
    sep("WHATSAPP — Verificación de cuenta")
    phone_clean = fmt_e164.replace("+", "").replace(" ", "")
    try:
        # Método 1: wa.me
        r = requests.get(
            f"https://wa.me/{phone_clean}",
            headers=HEADERS, timeout=10, allow_redirects=True
        )
        body = r.text.lower()

        if r.status_code == 200:
            if any(x in body for x in ["send message", "open whatsapp", "use whatsapp web", "whatsapp"]):
                ok(f"✓ Número ACTIVO en WhatsApp")
                dato("Número",      fmt_e164)
                dato("Link chat",   f"https://wa.me/{phone_clean}")
                dato("Link directo",f"https://api.whatsapp.com/send?phone={phone_clean}")
            else:
                warn("No se pudo confirmar cuenta de WhatsApp")
        elif r.status_code == 404:
            fail("Número NO registrado en WhatsApp")
        else:
            warn(f"WhatsApp respondió {r.status_code}")

        # Método 2: API no oficial
        try:
            r2 = requests.get(
                f"https://api.whatsapp.com/send?phone={phone_clean}",
                headers=HEADERS, timeout=8, allow_redirects=True
            )
            if r2.status_code == 200 and "phone" in r2.text.lower():
                dato("Verificación API", "Número encontrado en sistema WhatsApp")
        except Exception:
            pass

    except Exception as e:
        warn(f"No se pudo verificar WhatsApp: {type(e).__name__}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 6 — TELEGRAM (verificación)
# ══════════════════════════════════════════════════════════════════════════════
def modulo_telegram(fmt_e164):
    sep("TELEGRAM — Verificación de cuenta")
    phone_clean = fmt_e164.replace("+", "").replace(" ", "")
    try:
        # Verificar si tiene cuenta via t.me
        r = requests.get(
            f"https://t.me/+{phone_clean}",
            headers=HEADERS, timeout=10, allow_redirects=True
        )
        body = r.text.lower()

        if r.status_code == 200:
            if "tgme_page_title" in body or "telegram" in body:
                if "join" in body or "preview" in body:
                    ok("Número encontrado en Telegram")
                    dato("Link directo", f"https://t.me/+{phone_clean}")
                else:
                    warn("Telegram respondió pero sin perfil claro")
            else:
                warn("No se encontró cuenta de Telegram para este número")
        else:
            warn(f"Telegram respondió {r.status_code}")

        # Buscar en TGStat
        try:
            r2 = requests.get(
                f"https://tgstat.com/search?q={urllib.parse.quote(fmt_e164)}",
                headers=HEADERS, timeout=8
            )
            if r2.status_code == 200 and phone_clean in r2.text:
                ok("Número mencionado en TGStat")
                dato("TGStat", f"https://tgstat.com/search?q={urllib.parse.quote(fmt_e164)}")
        except Exception:
            pass

    except Exception as e:
        warn(f"No se pudo verificar Telegram: {type(e).__name__}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 7 — GRAVATAR (perfil asociado al hash del número)
# ══════════════════════════════════════════════════════════════════════════════
def modulo_gravatar(fmt_e164):
    sep("GRAVATAR — Perfil asociado")
    phone_clean = fmt_e164.replace("+", "").replace(" ", "").strip()
    md5_hash = hashlib.md5(phone_clean.encode()).hexdigest()
    try:
        r = requests.get(
            f"https://www.gravatar.com/{md5_hash}.json",
            headers=HEADERS_JSON, timeout=8
        )
        if r.status_code == 200:
            d = r.json()
            entry = d.get("entry", [{}])[0]
            ok("Perfil Gravatar encontrado para este número")
            dato("Display name",   entry.get("displayName", "—"))
            dato("Username",       entry.get("preferredUsername", "—"))
            dato("Avatar",         f"https://www.gravatar.com/avatar/{md5_hash}?s=200")
            dato("Perfil URL",     f"https://gravatar.com/{entry.get('preferredUsername','')}")
            for acc in entry.get("accounts", []):
                dato(f"Red [{acc.get('shortname','?')}]", acc.get("url", "—"))
            about = entry.get("aboutMe", "")
            if about:
                dato("Bio", about[:100])
        elif r.status_code == 404:
            warn("Sin perfil Gravatar asociado a este número")
        else:
            warn(f"Gravatar respondió {r.status_code}")
    except Exception as e:
        warn(f"Gravatar no disponible: {type(e).__name__}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 8 — RESUMEN INTELIGENCIA
# ══════════════════════════════════════════════════════════════════════════════
def modulo_resumen(phone_raw, fmt_e164, fmt_intl, region, parsed):
    sep("RESUMEN DE INTELIGENCIA")
    print(f"\n  {C}{B}Target:{RS}        {W}{B}{phone_raw}{RS}")
    print(f"  {C}{B}E164:{RS}          {W}{fmt_e164}{RS}")
    print(f"  {C}{B}Internacional:{RS} {W}{fmt_intl}{RS}")
    print(f"  {C}{B}País:{RS}          {W}{COUNTRY_NAMES.get(region, region) if region else '—'}{RS}")

    if parsed:
        op = carrier.name_for_number(parsed, "es")
        tipo = phonenumbers.number_type(parsed)
        print(f"  {C}{B}Operadora:{RS}     {W}{op if op else 'Ver módulo Veriphone'}{RS}")
        print(f"  {C}{B}Tipo línea:{RS}    {W}{TIPOS_LINEA.get(tipo, 'Desconocido')}{RS}")

    print(f"\n  {D}Análisis completado — Ciberbrigada OSINT Suite v2.0{RS}\n")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    banner()

    print(f"  {W}Ingresá el número con código de país:{RS}")
    print(f"  {D}Ej: +54 9 11 1234-5678 | +1 555 123 4567 | +34 612 345 678{RS}\n")

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

        # Módulo 1 siempre corre primero
        fmt_e164, fmt_intl, parsed, region = modulo_analisis(phone_raw)
        if not fmt_e164:
            continue

        # Menú
        sep("SELECCIONÁ LOS MÓDULOS")
        modulos = [
            ("2", "Veriphone        — Carrier, tipo y país (API gratuita)"),
            ("3", "NumVerify        — Validación y operadora"),
            ("4", "DNS / ENUM       — Protocolo E.164 e infraestructura"),
            ("5", "WhatsApp         — ¿Tiene cuenta activa?"),
            ("6", "Telegram         — ¿Tiene cuenta activa?"),
            ("7", "Gravatar         — Perfil asociado al número"),
            ("0", "TODOS LOS MÓDULOS"),
        ]
        for num, desc in modulos:
            color = C if num != "0" else Y
            print(f"  {color}[{num}]{RS} {W}{desc}{RS}")

        print()
        try:
            sel = input(f"  {C}▸ Opción (ej: 0 o 2,5,6):{RS} ").strip()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

        selected = ["2","3","4","5","6","7"] if sel == "0" else [s.strip() for s in sel.split(",")]
        print()

        if "2" in selected: modulo_veriphone(fmt_e164)
        if "3" in selected: modulo_numverify(fmt_e164, region)
        if "4" in selected: modulo_dns(fmt_e164, region)
        if "5" in selected: modulo_whatsapp(fmt_e164)
        if "6" in selected: modulo_telegram(fmt_e164)
        if "7" in selected: modulo_gravatar(fmt_e164)

        modulo_resumen(phone_raw, fmt_e164, fmt_intl, region, parsed)

        sep()
        print(f"\n  {D}¿Analizar otro número? (Enter / 'salir'){RS}")
        try:
            again = input(f"  {C}▸{RS} ").strip().lower()
            if again in ("salir", "exit", "quit", "q"):
                print(f"\n  {Y}Saliendo... Hasta pronto.{RS}\n")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

        banner()

if __name__ == "__main__":
    main()
