# Documentación de Perfiles de Navegadores

Este documento detalla la estructura de perfiles de varios navegadores web, incluyendo navegadores exóticos y de línea de comandos. Esta información es crucial para la migración efectiva de perfiles en Floorper.

## Navegadores Basados en Chromium

### Google Chrome

**Ubicación del perfil:**
- Windows: `%LOCALAPPDATA%\Google\Chrome\User Data\`
- macOS: `~/Library/Application Support/Google/Chrome/`
- Linux: `~/.config/google-chrome/`

**Estructura del perfil:**
- `Default/` - Perfil predeterminado
- `Profile 1/`, `Profile 2/`, etc. - Perfiles adicionales
- `Local State` - Configuración global
- `Preferences` - Preferencias del usuario (formato JSON)
- `Bookmarks` - Marcadores (formato JSON)
- `History` - Historial (base de datos SQLite)
- `Login Data` - Contraseñas guardadas (base de datos SQLite)
- `Cookies` - Cookies (base de datos SQLite)
- `Extensions/` - Extensiones instaladas

### Chromium

**Ubicación del perfil:**
- Windows: `%LOCALAPPDATA%\Chromium\User Data\`
- macOS: `~/Library/Application Support/Chromium/`
- Linux: `~/.config/chromium/`

**Estructura del perfil:** Idéntica a Chrome

## Navegadores Basados en Firefox

### Mozilla Firefox

**Ubicación del perfil:**
- Windows: `%APPDATA%\Mozilla\Firefox\Profiles\`
- macOS: `~/Library/Application Support/Firefox/Profiles/`
- Linux: `~/.mozilla/firefox/`

**Estructura del perfil:**
- `prefs.js` - Preferencias del usuario
- `places.sqlite` - Historial y marcadores
- `key4.db` - Contraseñas y certificados
- `cookies.sqlite` - Cookies
- `extensions/` - Extensiones instaladas
- `bookmarkbackups/` - Copias de seguridad de marcadores
- `sessionstore.jsonlz4` - Sesión guardada (pestañas abiertas)

## Navegadores Exóticos

### Dillo

**Ubicación del perfil:**
- Linux: `~/.dillo/`

**Estructura del perfil:**
- `dillorc` - Archivo de configuración (texto plano)
- `bookmarks.htm` - Marcadores (formato HTML)
- `cookies.txt` - Cookies (texto plano)
- `style.css` - Estilos personalizados

### NetSurf

**Ubicación del perfil:**
- Linux: `~/.config/netsurf/`

**Estructura del perfil:**
- `Cookies` - Cookies (formato binario)
- `Hotlist` - Marcadores (formato binario)
- `Options` - Opciones de configuración
- `URLs` - Historial de URLs visitadas

### Links2

**Ubicación del perfil:**
- Linux: `~/.links2/`

**Estructura del perfil:**
- `links.cfg` - Configuración (texto plano)
- `bookmarks.html` - Marcadores (formato HTML)
- `links.his` - Historial (texto plano)

## Navegadores de Texto

### Lynx

**Ubicación del perfil:**
- Linux: `~/.lynx/`

**Estructura del perfil:**
- `lynx.cfg` - Configuración global
- `lynx.lss` - Estilos de visualización
- `lynx_bookmarks.html` - Marcadores (formato HTML)
- `lynx_cookies` - Cookies (texto plano)

### ELinks

**Ubicación del perfil:**
- Linux: `~/.elinks/`

**Estructura del perfil:**
- `elinks.conf` - Configuración principal
- `bookmarks` - Marcadores (formato específico)
- `cookies` - Cookies (texto plano)
- `globhist` - Historial global
- `gotohist` - Historial de comandos "goto"

### W3M

**Ubicación del perfil:**
- Linux: `~/.w3m/`

**Estructura del perfil:**
- `config` - Configuración principal
- `bookmark.html` - Marcadores (formato HTML)
- `history` - Historial (texto plano)
- `cookie` - Cookies (texto plano)
- `passwd` - Contraseñas (texto plano)

## Navegadores Retro

### Netscape Navigator

**Ubicación del perfil:**
- Windows: `C:\Program Files\Netscape\Users\[username]\`
- Linux: `~/.netscape/`

**Estructura del perfil:**
- `bookmarks.html` - Marcadores (formato HTML)
- `cookies.txt` - Cookies (texto plano)
- `history.dat` - Historial (formato binario)
- `prefs.js` - Preferencias (JavaScript)

### NCSA Mosaic

**Ubicación del perfil:**
- Windows: `C:\Mosaic\`
- Linux: `~/.mosaicrc`

**Estructura del perfil:**
- `mosaic.hst` - Historial (texto plano)
- `mosaic.hot` - Hotlist/marcadores (texto plano)
- `mosaic.ini` - Configuración (texto plano)

## Proyectos de Inspiración para Migración de Perfiles

1. **Firefox Session Merger** (https://github.com/james-cube/firefox-session-merger)
   - Enfoque en la fusión de sesiones de Firefox
   - Manejo de archivos sessionstore.jsonlz4
   - Técnicas para combinar pestañas de múltiples sesiones

2. **Firefox Bookmarks Deduplicator** (https://github.com/james-cube/firefox-bookmarks-deduplicator)
   - Algoritmos para detectar y eliminar marcadores duplicados
   - Procesamiento de la base de datos places.sqlite
   - Preservación de la estructura de carpetas

3. **Firefox Bookmarks Merger** (https://github.com/james-cube/firefox-bookmarks-merger)
   - Técnicas para combinar colecciones de marcadores
   - Resolución de conflictos en la estructura de carpetas
   - Manejo de exportaciones HTML de marcadores

4. **Firefox History Merger** (https://github.com/crazy-max/firefox-history-merger)
   - Fusión de historiales de navegación
   - Manejo de la base de datos places.sqlite
   - Preservación de fechas y frecuencia de visitas

5. **Hekasoft Backup & Restore** (https://hekasoft.com/hekasoft-backup-restore/)
   - Enfoque en la creación y restauración de copias de seguridad
   - Soporte para múltiples navegadores
   - Interfaz de usuario intuitiva

6. **Browser Migration Tool** (https://github.com/Bm-Crafts/Browser-Migration-Tool/)
   - Enfoque multiplataforma
   - Detección automática de perfiles
   - Migración selectiva de componentes

7. **Bookmark Merger** (https://sourceforge.net/p/bookmark-merger/)
   - Especializado en la fusión de marcadores
   - Soporte para formatos HTML y JSON
   - Algoritmos de deduplicación

## Consideraciones para la Migración

1. **Seguridad**
   - Las contraseñas en navegadores modernos están cifradas
   - Algunos navegadores utilizan el almacén de claves del sistema
   - Los navegadores de texto suelen almacenar contraseñas en texto plano

2. **Compatibilidad de Formatos**
   - Conversión entre formatos de marcadores (HTML, JSON, texto plano)
   - Migración de bases de datos SQLite a otros formatos
   - Preservación de metadatos (fechas, etiquetas, carpetas)

3. **Detección de Perfiles**
   - Búsqueda en ubicaciones estándar y no estándar
   - Identificación de perfiles válidos vs. corruptos
   - Manejo de perfiles con nombres personalizados

4. **Fusión vs. Reemplazo**
   - Estrategias para fusionar contenido sin pérdida de datos
   - Resolución de conflictos (elementos duplicados, estructuras diferentes)
   - Opciones para preservar o reemplazar configuraciones

5. **Navegadores Exóticos**
   - Formatos propietarios o poco documentados
   - Limitaciones en la cantidad de datos almacenados
   - Conversión entre paradigmas diferentes (ej. navegadores de texto vs. gráficos)
