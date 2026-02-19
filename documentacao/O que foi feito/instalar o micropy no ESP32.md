Placa usada: ESP32-2432S028
1. Foi baixado o driver para MacOS (CH34xVCPDriver.pkg) e permitir como software de desenvolvedor (Ajustes do Sistema → Privacidade e Segurança). Link do driver: https://github.com/WCHSoftGroup/ch34xser_macos
2. ls /dev/cu.* (no terminal): mostra o ESP32 conectado 
![[Captura de Tela 2026-02-18 às 15.40.48.png]]
	/dev/cu.wchusbserial130 é o ESP32
3. Instalar as ferramentas necessárias: ![[Captura de Tela 2026-02-18 às 15.42.42.png]]
	esptool: grava firmware no ESP32
	mpremote: terminal + transferência de arquivos
4. Colocar o ESP32 em modo de gravação:
	1.  Pressionar e segurar BOOT
	2. Apertar RESET
	3. Soltar RESET
	4. Soltar BOOT
	Imagem identificando os botões BOOT e RESET: 
	![[Pasted image 20260218164351.png]]
	fica ao lado do ESP
5. Apagar completamente a flash![[Captura de Tela 2026-02-18 às 16.46.34.png]]
	codigo: esptool --chip esp32 --port /dev/cu.wchusbserial130 erase-flash
	remove o firmware de fabrica
6. Instalar o MicroPython 
	link download: https://micropython.org/resources/firmware/ESP32_GENERIC-20251209-v1.27.0.bin
	![[Captura de Tela 2026-02-18 às 16.52.05.png]]
	 código usado: esptool --chip esp32 \
--port /dev/cu.wchusbserial130 \
--baud 460800 \
--before default-reset \
--after hard-reset \
write-flash -z 0x1000 ~/Downloads/ESP32_GENERIC-20251209-v1.27.0.bin
7. Acessar o MicroPython![[Captura de Tela 2026-02-18 às 16.55.16.png]]
	codigo usado para conectar o micropython: mpremote connect /dev/cu.wchusbserial130
	os.listdir() lista os diretorios na memoria do microcontrolador
```python
	from machine import Pin
	bl = Pin(21, Pin.OUT)
	bl.value(1)
	#acende a tela do CYD(cheap yellow display nome popular do modelo usado)
```
	