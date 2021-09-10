# rt-05

Прототип консольного приложения для работы с микропроцессорным регулятором ТЭСМАРТ РТ-05.
Данные для подключения берутся из файла config.toml

### Пример файла конфигупации config.toml
```toml
[MAIN]
mode = "serial"

[DEVICE]
slave_id = 1

[SERIAL]
port = "/dev/ttys001" # или COM1 для Windows
baudrate = 9600
parity = "N"
bytesize = 8
stopbits = 1
```
