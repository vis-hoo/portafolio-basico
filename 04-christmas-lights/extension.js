import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import Clutter from 'gi://Clutter';
import St from 'gi://St';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const BULB_SPACING = 46;
const BULB_RADIUS = 13;
const STRIP_HEIGHT = 58;
const GAP_BELOW_PANEL = 2; // separación entre el panel y el cable
const FRAME_MS = 40;

const COLORS = [
    [0.92, 0.18, 0.20],
    [0.20, 0.80, 0.32],
    [0.98, 0.72, 0.15],
    [0.25, 0.55, 0.95],
    [0.85, 0.30, 0.85],
];

const LightsActor = GObject.registerClass(
class LightsActor extends St.DrawingArea {
    _init(extension) {
        super._init({
            style_class: 'christmas-lights-actor',
            reactive: true,
            x_expand: true,
        });
        this._extension = extension;
        this._time = 0;
        this._phase = Math.random() * Math.PI * 2;
        this._timeout = 0;
        this.connect('repaint', () => this._draw());
    }

    start() {
        this._timeout = GLib.timeout_add(GLib.PRIORITY_DEFAULT, FRAME_MS, () => {
            this._time += FRAME_MS / 1000.0;
            this.queue_repaint();
            return GLib.SOURCE_CONTINUE;
        });
    }

    stop() {
        if (this._timeout) {
            GLib.source_remove(this._timeout);
            this._timeout = 0;
        }
    }

    vfunc_button_press_event(event) {
        if (event.get_button() === 3 && this._extension) {
            this._extension.toggleMenu();
            return Clutter.EVENT_STOP;
        }
        return Clutter.EVENT_PROPAGATE;
    }

    _brightness(index) {
        const t = this._time * 1.4 + this._phase;
        const wave = Math.sin(t + index * 0.55);
        const pulse = 0.5 + 0.5 * wave; // 0..1
        // Rango amplio: de apagado grisáceo (0.12) a pleno brillo (1.0).
        return 0.12 + 0.88 * pulse;
    }

    _bulbColor([r, g, b], glow) {
        // Al bajar el brillo, el color tiende a un gris apagado en vez de
        // solo oscurecerse: mezcla hacia gris cuando glow es bajo.
        const mix = Math.max(0, Math.min(1, glow)); // 0 = apagado, 1 = vivo
        const grey = 0.22;
        const t = mix * mix; // acentúa la diferencia
        const outR = grey + (r - grey) * t;
        const outG = grey + (g - grey) * t;
        const outB = grey + (b - grey) * t;
        const dim = 0.25 + 0.75 * mix; // oscurece además el apagado
        return [outR * dim, outG * dim, outB * dim];
    }

    _draw() {
        const cr = this.get_context();
        const [width] = this.get_surface_size();
        const wireY = 1;
        const sag = 7;
        const bulbY = 26;

        // Cable colgante
        cr.setLineWidth(2.5);
        cr.setSourceRGB(0.35, 0.38, 0.45);
        cr.moveTo(0, wireY);
        const steps = Math.max(2, Math.floor(width / 12));
        for (let i = 0; i <= steps; i++) {
            const x = (width * i) / steps;
            const y = wireY + sag * Math.sin((Math.PI * i) / steps);
            cr.lineTo(x, y);
        }
        cr.stroke();

        // Focos
        const count = Math.max(1, Math.floor(width / BULB_SPACING));
        for (let i = 0; i < count; i++) {
            const x = (i + 0.5) * (width / count);
            const color = COLORS[i % COLORS.length];
            const glow = this._brightness(i);
            const [br, bg, bb] = this._bulbColor(color, glow);

            // Casquillo
            cr.setSourceRGB(0.45, 0.48, 0.55);
            cr.rectangle(x - 5, wireY + sag * 0.5 + 2, 10, 7);
            cr.fill();

            // Halo: solo cuando la luz está encendida
            if (glow > 0.45) {
                const halo = (glow - 0.45) / 0.55;
                cr.setSourceRGBA(color[0], color[1], color[2], 0.22 * halo);
                cr.arc(x, bulbY, BULB_RADIUS * 2.1, 0, Math.PI * 2);
                cr.fill();
            }

            // Foco
            cr.setSourceRGBA(br, bg, bb, 1.0);
            cr.arc(x, bulbY, BULB_RADIUS, 0, Math.PI * 2);
            cr.fill();

            // Reflejo interno: también se apaga
            if (glow > 0.5) {
                cr.setSourceRGBA(1, 1, 1, 0.4 * (glow - 0.5) / 0.5);
                cr.arc(x - BULB_RADIUS * 0.3, bulbY - BULB_RADIUS * 0.3,
                    BULB_RADIUS * 0.35, 0, Math.PI * 2);
                cr.fill();
            }
        }

        cr.$dispose();
    }
});

export default class ChristmasLightsExtension extends Extension {
    enable() {
        this._menu = null;

        this._actor = new LightsActor(this);
        this._actor.set_height(STRIP_HEIGHT);

        Main.layoutManager.uiGroup.add_child(this._actor);
        this._actor.start();

        // Menú contextual (clic derecho)
        this._menu = new PopupMenu.PopupMenu(this._actor, 0.0, St.Side.TOP);
        this._menu.actor.add_style_class_name('christmas-lights-menu');
        const closeItem = new PopupMenu.PopupMenuItem('Cerrar luces');
        closeItem.connect('activate', () => this.disable());
        this._menu.addMenuItem(closeItem);
        Main.uiGroup.add_child(this._menu.actor);
        this._menu.actor.hide();
        this._menuManager = new PopupMenu.PopupMenuManager({actor: this._actor});
        this._menuManager.addMenu(this._menu);

        this._reposition();
        this._monitorsChangedId = Main.layoutManager.connect(
            'monitors-changed', () => this._reposition());
    }

    toggleMenu() {
        if (this._menu)
            this._menu.toggle();
    }

    _reposition() {
        if (!this._actor)
            return;
        const monitor = Main.layoutManager.primaryMonitor;
        const panelHeight = Main.panel.height;
        // Cuelga justo debajo del panel superior.
        this._actor.set_position(monitor.x, monitor.y + panelHeight + GAP_BELOW_PANEL);
        this._actor.set_width(monitor.width);
    }

    disable() {
        if (this._monitorsChangedId) {
            Main.layoutManager.disconnect(this._monitorsChangedId);
            this._monitorsChangedId = 0;
        }
        if (this._menu) {
            this._menu.destroy();
            this._menu = null;
        }
        this._menuManager = null;
        if (this._actor) {
            this._actor.stop();
            this._actor.destroy();
            this._actor = null;
        }
    }
}
