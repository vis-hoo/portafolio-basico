# 03 - Calculator

Calculadora científica de escritorio para Linux, empaquetada como Flatpak. Hecha con Python, GTK4 y libadwaita.

Evalúa la expresión en tiempo real mientras escribes: no hay botón "convertir" obligatorio.

## Características

- Operaciones básicas: suma, resta, multiplicación, división, módulo (%).
- Científicas: potencias (`^`), raíz cuadrada, seno/coseno/tangente, log (base 10), ln, factorial (`!`).
- Paréntesis, decimales, constantes `π` y `e`, y `Ans` (último resultado confirmado con `=`).
- Interruptor Deg/Rad que recalcula al instante.
- Resultado en decimal y, cuando existe, su fracción equivalente (ej. `0.5` → `1/2`).
- División por cero o expresión inválida: muestra "Error" en rojo en vivo.
- `=` confirma la expresión, guarda el resultado en `Ans` y la deja bloqueada (para seguir, usa `C`).
- Historial simple de cálculos con botón para vaciarlo.
- Solo botones: teclado físico deshabilitado.
- Sin dependencias más allá del runtime de GNOME.

## Construir e instalar

Requisitos: Fedora con `flatpak` y `flatpak-builder` instalados.

```bash
# Instalar el SDK de GNOME necesario para compilar
flatpak install --user flathub org.gnome.Platform//50 org.gnome.Sdk//50

# Compilar e instalar (--disable-rofiles-fuse evita un bug de FUSE en Fedora)
flatpak-builder --user --install --force-clean --disable-rofiles-fuse build com.github.vishoo.calculator.yml

# Ejecutar
flatpak run com.github.vishoo.calculator
```

## Estructura

| Archivo | Propósito |
|---------|-----------|
| `engine.py` | Motor de cálculo (léxico, parser, evaluador) |
| `calculator.py` | Interfaz GTK4 |
| `test_engine.py` | Pruebas del motor (`python3 -m unittest test_engine`) |
| `com.github.vishoo.calculator.yml` | Manifest de Flatpak |
| `com.github.vishoo.calculator.desktop` | Entrada de menú |
| `com.github.vishoo.calculator.metainfo.xml` | Metadatos AppStream |
| `com.github.vishoo.calculator.svg` | Icono |

## Licencia

[MIT](LICENSE) © 2026 vis-hoo
