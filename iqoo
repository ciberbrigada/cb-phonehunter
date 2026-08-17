# 📱 CB-PhoneHunter

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0-cyan?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/OSINT-Phone-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/free-sin%20API%20key-brightgreen?style=for-the-badge"/>
</p>

<p align="center">
  <b>Reconocimiento OSINT de números telefónicos en fuentes abiertas</b><br/>
  Parte de la <a href="https://ciberbrigada.com">Ciberbrigada OSINT Suite</a>
</p>

---

## ¿Qué hace?

CB-PhoneHunter analiza un número de teléfono en múltiples fuentes abiertas y gratuitas:

- ✅ Validación y formato del número (E164, internacional, nacional)
- ✅ País, región, operadora y zona horaria
- ✅ Tipo de línea (móvil, fijo, VoIP, etc.)
- ✅ Verificación en Truecaller (nombre del dueño)
- ✅ Verificación en WhatsApp (¿tiene cuenta activa?)
- ✅ Links de verificación en Telegram
- ✅ GetContact (nombres con los que fue guardado)
- ✅ Google Dorks automáticos (12 búsquedas)
- ✅ Links directos a 10 plataformas de búsqueda
- ✅ Geolocalización por país y operadora

**100% gratuito · Sin API keys · Sin registro · Sin login**

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/ciberbrigada/cb-phonehunter
cd cb-phonehunter

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python3 cb_phone_hunter.py
```

### Kali Linux / Parrot OS / Ubuntu

```bash
git clone https://github.com/ciberbrigada/cb-phonehunter
cd cb-phonehunter
pip install -r requirements.txt
python3 cb_phone_hunter.py
```

### Windows

```cmd
git clone https://github.com/ciberbrigada/cb-phonehunter
cd cb-phonehunter
pip install -r requirements.txt
python cb_phone_hunter.py
```

---

## 🔄 Mantener actualizado

```bash
cd cb-phonehunter
git pull
```

---

## Uso

```bash
python3 cb_phone_hunter.py
```

```
▸ Teléfono: +54 9 11 1234-5678

── ANÁLISIS DEL NÚMERO ──
  ▸ Número internacional: +54 9 11 1234-5678
  ▸ Formato E164:         +541112345678
  ▸ País / Región:        Argentina
  ▸ Operadora:            Claro
  ▸ Tipo de línea:        MÓVIL

[0] TODOS LOS MÓDULOS
[1] Análisis del número
[2] Truecaller
[3] WhatsApp
[4] Telegram
[5] GetContact
[6] Google Dorks
[7] Redes Sociales
[8] Geolocalización
```

---

## Módulos

| # | Módulo | Descripción |
|---|--------|-------------|
| 1 | Análisis | Formato, país, operadora, zona horaria, tipo de línea |
| 2 | Truecaller | Nombre del dueño registrado |
| 3 | WhatsApp | Verifica si tiene cuenta activa + link directo |
| 4 | Telegram | Links de verificación y búsqueda |
| 5 | GetContact | Nombres con los que fue guardado por otros usuarios |
| 6 | Google Dorks | 12 búsquedas automáticas en Google |
| 7 | Redes Sociales | Links directos a 10 plataformas de búsqueda |
| 8 | Geolocalización | País, región y operadora via APIs públicas |

---

## Formato de entrada

```
+54 9 11 1234-5678    (Argentina móvil)
+1 555 123 4567       (Estados Unidos)
+34 612 345 678       (España)
+55 11 91234-5678     (Brasil)
```

Siempre incluí el **código de país** con el símbolo `+`.

---

## Requisitos

- Python 3.8+
- requests
- colorama
- phonenumbers
- Conexión a internet

---

## ⚠️ Aviso Legal

Esta herramienta es para uso **exclusivamente legal, ético y educativo**.  
El uso de esta herramienta para actividades ilegales queda bajo la responsabilidad del usuario.  
Ciberbrigada no se hace responsable del mal uso de esta herramienta.

---

## 🛡️ Ciberbrigada OSINT Suite

- 📧 **CB-EmailHunter** — Email OSINT → [ver repo](https://github.com/ciberbrigada/cb-emailhunter)
- 👤 **CB-UserHunter** — Username OSINT → [ver repo](https://github.com/ciberbrigada/cb-userhunter)
- 📱 **CB-PhoneHunter** — Phone OSINT *(este repositorio)*
- 🌐 **CB-DomainHunter** — OSINT de dominios e IPs *(próximamente)*
- 📸 **CB-InstaHunter** — Instagram OSINT *(próximamente)*

---

<p align="center">
  <a href="https://ciberbrigada.com">ciberbrigada.com</a> ·
  <a href="https://github.com/ciberbrigada">GitHub</a> ·
  <a href="https://www.linkedin.com/company/ciberbrigada/">LinkedIn</a>
  <br/><br/>
  <sub>by: Fgunther</sub>
</p>
