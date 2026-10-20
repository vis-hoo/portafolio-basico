# 02 - Border Radius Previewer

Herramienta web para previsualizar valores de `border-radius` en tiempo real. Ajusta cada esquina con un slider y copia el CSS resultante.

Hecho con HTML, CSS y JavaScript puros. Sin dependencias ni build.

## Características

- 4 sliders independientes, uno por esquina (0–100 px).
- Botón "Vincular esquinas": sincroniza las 4 esquinas con un mismo valor.
- Vista previa en vivo de la forma resultante.
- Código CSS generado en tiempo real con botón de copiar al portapapeles.
- Tema oscuro.

## Uso

Abrir `index.html` en un navegador, o servirlo con cualquier servidor estático:

```bash
python3 -m http.server 8000
# luego abrir http://localhost:8000
```

## Estructura

| Archivo | Propósito |
|---------|-----------|
| `index.html` | Estructura de la página |
| `style.css` | Estilos y tema oscuro |
| `app.js` | Lógica de sliders, vinculación y copia |

## Licencia

[MIT](LICENSE) © 2026 vis-hoo
