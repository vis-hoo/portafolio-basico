# 01 - Bin2Dec

Conversor binario ↔ decimal en tiempo real. Aplicación de escritorio para Linux (empaquetada como Flatpak), hecha con Python, GTK4 y libadwaita.

Escribe en cualquiera de los dos campos y el otro se actualiza al instante. La entrada inválida se pinta en rojo.

## Características

- Conversión bidireccional en tiempo real (sin botón de convertir).
- Soporta hasta 64 bits.
- Dígitos binarios agrupados de 4 en 4 para legibilidad.
- Validación visual: la entrada inválida aparece en rojo.
- Botones de limpiar y copiar resultado al portapapeles.

## Construir e instalar

Requisitos: Fedora con `flatpak` y `flatpak-builder` instalados.

```bash
# Instalar el SDK de GNOME necesario para compilar
flatpak install --user flathub org.gnome.Platform//50 org.gnome.Sdk//50

# Compilar e instalar (--disable-rofiles-fuse evita un bug de FUSE en Fedora)
flatpak-builder --user --install --force-clean --disable-rofiles-fuse build com.github.vishoo.bin2dec.yml

# Ejecutar
flatpak run com.github.vishoo.bin2dec
```

## Estructura

| Archivo | Propósito |
|---------|-----------|
| `bin2dec.py` | Aplicación (Python + GTK4 + libadwaita) |
| `com.github.vishoo.bin2dec.yml` | Manifest de Flatpak |
| `com.github.vishoo.bin2dec.desktop` | Entrada de menú |
| `com.github.vishoo.bin2dec.metainfo.xml` | Metadatos AppStream |
| `com.github.vishoo.bin2dec.svg` | Icono |

## Licencia

[MIT](LICENSE) © 2026 vishoo
