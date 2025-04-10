import board
import digitalio
from kmk.bootcfg import bootcfg

# Light up an LED during boot for some feedback.
meta_led = digitalio.DigitalInOut(board.GP28)
meta_led.switch_to_output(value=True)

# Fn+Esc is a normal reset (see code.py) but Fn+Shift+Esc will allow programming.
bootcfg(
    sense=board.GP22, source=board.GP11, # Right shift key during boot enables serial and usb_drive.
    storage=False,
    cdc_console=False,
    midi=False,
    boot_device=1, # Let the keyboard be used in the BIOS.
    consumer_control=True,
    keyboard=True,
    mouse=True,
)

# Put things back how they were for code.py to run.
meta_led.value = 0
meta_led.deinit()