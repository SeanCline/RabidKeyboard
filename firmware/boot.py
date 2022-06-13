import supervisor
import board
import digitalio
import storage
import usb_cdc, usb_hid, usb_midi

# KMK is big. Give it enough stack space.
supervisor.set_next_stack_limit(4096 + 4096)

# Keep all the mass storage device and COM port enabled when Shift is held during boot.
# This lets Fn+Esc be a normal reset (see code.py) but Fn+Shift+Esc be a boot for programming.
col = digitalio.DigitalInOut(board.GP11)
row = digitalio.DigitalInOut(board.GP22)
col.switch_to_input(pull=digitalio.Pull.DOWN)
row.switch_to_output(value=True)

if not col.value:
    storage.disable_usb_drive()
    usb_cdc.disable()
    usb_midi.disable()

# Let the keyboard be used in the BIOS.
usb_hid.enable(boot_device=1)

# Put things back how they were for code.py to run.
row.deinit()
col.deinit()