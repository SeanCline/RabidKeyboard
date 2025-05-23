# RabidKeyboard
# https://sdcline.com/RabidKeyboard
import board
import time
import digitalio
import pwmio
import math
import supervisor
import microcontroller

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import DiodeOrientation
from kmk.scanners.keypad import MatrixScanner
from kmk.keys import KC
from kmk.modules.layers import Layers
from kmk.extensions import Extension
from kmk.extensions.media_keys import MediaKeys
from kmk.extensions.lock_status import LockStatus
from kmk.modules.dynamic_sequences import DynamicSequences
from kmk.modules.mouse_jiggler import MouseJiggler

# Set up the key matrix.
class KMKRabidKeyboard(KMKKeyboard):
    def __init__(self):
        super().__init__()

        self.col_pins = (
            board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6,
            board.GP7, board.GP8, board.GP9, board.GP10, board.GP11, board.GP12, board.GP13,
            board.GP14, board.GP15, board.GP16
        )

        self.row_pins = (
            board.GP26, board.GP25, board.GP24, board.GP23, board.GP22, board.GP20
        )

        self.diode_orientation = DiodeOrientation.ROW2COL
        
        self.matrix = MatrixScanner(
            column_pins=self.col_pins,
            row_pins=self.row_pins,
            columns_to_anodes=self.diode_orientation,
            interval=0.01,
            debounce_threshold=3,
            max_events=64
        )

keyboard = KMKRabidKeyboard()

# Set up the mappings in each layer.
keyboard.modules.append(Layers())
keyboard.extensions.append(MediaKeys())

dyn_seq = DynamicSequences(
    slots=10, # The number of sequence slots to use
    timeout=60000,  # Maximum time to spend in record or config mode before stopping automatically, milliseconds
    key_interval=25,  # Milliseconds between key events while playing
    use_recorded_speed=False,  # Whether to play the sequence at the speed it was typed
)
keyboard.modules.append(dyn_seq)

# Set up the Mouse Jiggler.
jiggler = MouseJiggler()
keyboard.modules.append(jiggler)

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
SEQ_REC = KC.RECORD_SEQUENCE()
SEQ_STP = KC.STOP_SEQUENCE()
SEQ_PLY = KC.PLAY_SEQUENCE()
SEQ_SET = KC.SET_SEQUENCE
fn_layer = [
    KC.RESET, KC.NO, KC.BOOTLOADER, KC.NO, KC.NO, KC.NO, KC.MPLY, KC.MSTP, KC.MPRV, KC.MNXT, MetaLock, KC.MUTE, KC.VOLD, KC.VOLU, KC.NO, KC.MJ_TOGGLE, KC.NO,
    SEQ_REC, SEQ_SET(1), SEQ_SET(2), SEQ_SET(3),  SEQ_SET(4),  SEQ_SET(5),  SEQ_SET(6),  SEQ_SET(7), SEQ_SET(8), SEQ_SET(9), SEQ_SET(0), KC.NO, KC.NO, SEQ_STP, KC.NO, KC.NO, KC.NO,
    KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO,
    KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, SEQ_PLY, KC.NO, KC.NO, KC.NO, KC.NO,
    KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO,
    KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO, KC.NO,
]

# Finish up the layers.
keyboard.keymap = [base_layer, metalock_layer, fn_layer]

# Define an extension that keeps the Caps, Scroll, and Meta lock LEDs synched with the keyboard/HID state.
class LockStatusLeds(LockStatus):
    def __init__(self, caps_led : Pin, meta_led : Pin, scroll_led : Pin, jiggler : MouseJiggler = None):
        super().__init__()
        self.caps_led = digitalio.DigitalInOut(caps_led)
        self.caps_led.direction = digitalio.Direction.OUTPUT
        self.meta_led = digitalio.DigitalInOut(meta_led)
        self.meta_led.direction = digitalio.Direction.OUTPUT
        self.scroll_led = pwmio.PWMOut(scroll_led)
        self._jiggler = jiggler
        self._prev_jiggle_state = None
        self._last_fade_tick = 0
        self.fade_interval = .01
        
    def after_hid_send(self, sandbox):
        super().after_hid_send(sandbox)
        
        # Throttle status led updates.
        ticks_ms = supervisor.ticks_ms()
        ticks_since_last_fade = ticks_ms - self._last_fade_tick
        if (ticks_since_last_fade > 0 and ticks_since_last_fade < 30):
            return
        self._last_fade_tick = ticks_ms

        # Caps Lock
        self.caps_led.value = self.get_caps_lock()
        
        # Meta Lock
        self.meta_led.value = (sandbox.active_layers[0] == 1)
        
        # Scroll Lock & Jiggle
        jiggle_on = self._jiggler is not None and self._jiggler.is_jiggling
        if jiggle_on:
            fade_ticks = ticks_ms & 0xFFFF # Truncate the high bits so conversion to float doesn't lose precision.
            self.scroll_led.duty_cycle = int((math.sin(fade_ticks*self.fade_interval)+1)/2 * 65535)
            self._prev_jiggle_state = jiggle_on
        elif jiggle_on != self._prev_jiggle_state:
            self.scroll_led.duty_cycle = 0
            self._prev_jiggle_state = jiggle_on
        else:
            self.scroll_led.duty_cycle = self.get_scroll_lock() * 65535

keyboard.extensions.append(LockStatusLeds(board.A3, board.GP28, board.GP27, jiggler))

def wait_for_usb():
    """https://github.com/adafruit/circuitpython/issues/6018"""
    while not supervisor.runtime.usb_connected:
        time.sleep(0.2)

def main():
    try:
        wait_for_usb()
        keyboard.go()
    except Exception as e:
        time.sleep(1)
        microcontroller.reset()

if __name__ == '__main__':
    main()