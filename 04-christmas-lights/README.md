# 04 - Christmas Lights

Extensión de GNOME Shell que cuelga una guirnalda de luces navideñas animadas de la parte superior de la pantalla, por encima de la barra y de todas las ventanas.

## Características

- Luces dibujadas como actor del shell: se superponen a la barra superior y a cualquier aplicación.
- Franja a todo el ancho de la pantalla, anclada al borde superior.
- Focos de colores con parpadeo suave tipo luz incandescente (onda recorriendo la franja, no encendido/apagado).
- Cable con curva colgante, casquillos y resplandor por foco.
- Clic derecho abre un menú con "Cerrar luces".

## Instalación

Requiere GNOME Shell 50 (probado en 50.6 sobre Fedora).

```bash
# Copiar la extensión al directorio de usuario
mkdir -p ~/.local/share/gnome-shell/extensions/christmas-lights@vishoo.github.com
cp metadata.json extension.js stylesheet.css \
   ~/.local/share/gnome-shell/extensions/christmas-lights@vishoo.github.com/

# Habilitar (en Wayland, cierra sesión y vuelve a entrar antes de esto)
gnome-extensions enable christmas-lights@vishoo.github.com
```

En Wayland, GNOME Shell no se puede reiniciar sin cerrar sesión, así que la extensión recién copiada aparece después de volver a iniciar sesión. Para deshabilitarla:

```bash
gnome-extensions disable christmas-lights@vishoo.github.com
```

## Nota sobre el desarrollo

Este proyecto nació como app de escritorio (Flatpak con Python y GTK4), pero tanto "siempre arriba" como la posición absoluta son imposibles en Wayland para aplicaciones normales: el compositor las ignora. La única vía con integración real es una extensión de GNOME Shell, y eso es lo que hay aquí.

## Estructura

| Archivo | Propósito |
|---------|-----------|
| `metadata.json` | Metadatos de la extensión (uuid, nombre, versión de shell) |
| `extension.js` | Lógica: actor de luces, animación y menú |
| `stylesheet.css` | Estilos del actor y del menú |
| `LICENSE` | Licencia MIT |

## Licencia

[MIT](LICENSE) © 2026 vis-hoo
