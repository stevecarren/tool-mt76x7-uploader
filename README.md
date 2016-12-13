#MT76x7 Uploader
This tool provides the functionality to flash the bootloader and the firmware of the MT76x7 platform, which includes the firmware of both CM4 and the N9 processors.

##Usage
```
-c COM_PORT      COM port, can be COM1, COM2, ..., COMx
-f BIN_FILE      path of the bin file to be uploaded
-t FLASH_TARGET  target to be flashed (cm4 | ldr | n9)
```
##Example
Windows:
```
python .\upload.py -c com24 -f sample.bin -t cm4
```
Linux/macOS:
```
python ./upload.py -c /dev/tty.usbmodem1412 -f sample.bin -t cm4
```