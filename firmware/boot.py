import board
import digitalio
import storage
import usb_cdc, usb_hid, usb_midi

# Light up an LED during boot for some feedback.
meta_led = digitalio.DigitalInOut(board.GP28)
meta_led.switch_to_output(value=True)

# Keep the mass storage device and COM port enabled when Shift is held during boot.
# This lets Fn+Esc be a normal reset (see code.py) but Fn+Shift+Esc be a boot for programming.
shift_col = digitalio.DigitalInOut(board.GP11)
shift_row = digitalio.DigitalInOut(board.GP22)
shift_col.switch_to_input(pull=digitalio.Pull.DOWN)
shift_row.switch_to_output(value=True)

if not shift_col.value:
    storage.disable_usb_drive()
    usb_cdc.disable()

usb_midi.disable()

# Let the keyboard be used in the BIOS.
hid_devices = (usb_hid.Device.KEYBOARD, usb_hid.Device.CONSUMER_CONTROL)
usb_hid.enable(hid_devices, boot_device=1)

# Put things back how they were for code.py to run.
meta_led.value = 0
meta_led.deinit()
shift_row.deinit()
shift_col.deinit()

# Allow writes to flash.
storage.remount("/", False)