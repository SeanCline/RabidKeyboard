# RabidKeyboard
# https://sdcline.com/RabidKeyboard
import board
import digitalio

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.modules.layers import Layers
from kmk.extensions import Extension
from kmk.extensions.media_keys import MediaKeys
from kmk.extensions.lock_status import LockStatus

# Set up the key matrix.
keyboard = KMKKeyboard()

keyboard.col_pins = (
    board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6,
    board.GP7, board.GP8, board.GP9, board.GP10, board.GP11, board.GP12, board.GP13,
    board.GP14, board.GP15, board.GP16
)

keyboard.row_pins = (
    board.GP26, board.GP25, board.GP24, board.GP23, board.GP22, board.GP20
)

keyboard.diode_orientation = DiodeOrientation.ROW2COL

# Set up the mappings in each layer.
keyboard.modules.append(Layers())
keyboard.extensions.append(MediaKeys())

# Define the layer-switching keys.
Fn = KC.MO(2)
MetaLock = KC.TG(1)

# Layer 0: Base layer is the typical key map.
base_layer = [
    KC.ESC, KC.NO, KC.F1, KC.F2, KC.F3, KC.F4, KC.F5, KC.F6, KC.F7, KC.F8, KC.F9, KC.F10, KC.F11, KC.F12, KC.PSCR, KC.SLCK, KC.BRK,
    KC.GRV, KC.N1, KC.N2, KC.N3, KC.N4, KC.N5, KC.N6, KC.N7, KC.N8, KC.N9, KC.N0, KC.MINS, KC.EQL, KC.BSPC, KC.INS, KC.HOME, KC.PGUP,
    KC.TAB, KC.Q, KC.W, KC.E, KC.R, KC.T, KC.Y, KC.U, KC.I, KC.O, KC.P, KC.LBRC, KC.RBRC, KC.BSLS, KC.DEL, KC.END, KC.PGDN,
    KC.CAPS, KC.A, KC.S, KC.D, KC.F, KC.G, KC.H, KC.J, KC.K, KC.L, KC.SCLN, KC.QUOT, KC.ENT, KC.NO, KC.NO, KC.NO, KC.NO,
    KC.LSFT, KC.Z, KC.X, KC.C, KC.V, KC.B, KC.N, KC.M, KC.COMM, KC.DOT, KC.SLSH, KC.RSFT, KC.NO, KC.NO, KC.NO, KC.UP, KC.NO,
    KC.LCTL, KC.LGUI, KC.LALT, KC.NO, KC.NO, KC.NO, KC.SPC, KC.NO, KC.NO, KC.NO, KC.RALT, KC.RGUI, Fn, KC.RCTL, KC.LEFT, KC.DOWN, KC.RIGHT,
]

# Layer 1: Meta-lock layer disables RGUI/LGUI but is otherwise transparent to the base layer.
def transparentUnlessMeta(kc):
    return KC.NO if (kc == KC.LGUI or kc == KC.RGUI) else KC.TRNS

metalock_layer = [transparentUnlessMeta(kc) for kc in base_layer]

# Layer 2: Active while Fn key is held.
fn_layer = [KC.RESET, KC.NO, KC.BOOTLOADER, KC.NO, KC.NO, KC.NO, KC.MPLY, KC.MSTP, KC.MPRV, KC.MNXT, MetaLock, KC.MUTE, KC.VOLD, KC.VOLU] + [KC.NO]*73

# Finish up the layers.
keyboard.keymap = [base_layer, metalock_layer, fn_layer]

# Define an extension that keeps the Caps, Scroll, and Meta lock LEDs synched with the keyboard/HID state.
class LockLeds(Extension):
    def __init__(self, ls_ext : LockStatus, caps_led : Pin, meta_led : Pin, scroll_led : Pin):
        self.ls = ls_ext
        self.caps_out = digitalio.DigitalInOut(caps_led)
        self.caps_out.direction = digitalio.Direction.OUTPUT
        self.meta_out = digitalio.DigitalInOut(meta_led)
        self.meta_out.direction = digitalio.Direction.OUTPUT
        self.scroll_out = digitalio.DigitalInOut(scroll_led)
        self.scroll_out.direction = digitalio.Direction.OUTPUT
    def during_bootup(self, _):
        return
    def before_hid_send(self, _):
        return
    def after_hid_send(self, _):
        return
    def before_matrix_scan(self, _):
        return
    def after_matrix_scan(self, keyboard):
        self.caps_out.value = self.ls.get_caps_lock()
        self.meta_out.value = (keyboard.active_layers[0] == 1)
        self.scroll_out.value = self.ls.get_scroll_lock()

ls_ext = LockStatus()
keyboard.extensions.append(ls_ext)
keyboard.extensions.append(LockLeds(ls_ext, board.A3, board.GP28, board.GP27))

if __name__ == '__main__':
    keyboard.debug_enabled = True
    keyboard.go()