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

### Pelo Thonny:
1. Pré-requisitos

- **Thonny IDE:** Baixe e instale em thonny.org.
- **Cabo USB:** Certifique-se de que o cabo USB para Micro USB (ou USB-C, dependendo da versão) seja de dados e não apenas de carga.
- **Firmware MicroPython:** Baixe a versão estável mais recente do firmware para ESP32 (GENERIC ESP32) em micropython.org/download/ESP32_GENERIC/. ![GitHub](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAb1BMVEX///8kKS74+PgsMTY+Q0f8/Pzw8PGRk5ZNUVXr6+xDSEzCxMUpLjLV1tYuMzc/Q0i3ubuUl5lbX2NTV1uLjpFKTlKxs7Xh4uOFh4rn5+h3en1vcnZ9gIPc3d6/wcJzd3o3PECmqKpjZ2rOz9CfoaRP5W5KAAABU0lEQVQ4jW1T7aKCIAzdEEUTSUuzLMtuvf8zXtiQVDx/lJ3DvgEIEPU9l1rL/F4LiFEMCQYkj2JDC6VxhaRJl3x2xgin7MePMuYRD7cQftrjrcL7ELk9nNt8yXXtyRm5mquzXADKA6LpzgZRlgBPZ1WO7yn/yrmqyGdGn95Zjav2hbNghZHMV3uNG3DZCigEmhRq+pmyrUAcifj4CO+49xciWqAe6p3pCJrNH1ATp5gH6KghQLrDnoB8GxaYPYFkhpONipjrl+wI61hQ8tB5EvYb4eTL5Ebhd8u/2f4EYfhvvWJpw9ZJ0LQfb5uxbMKi3pp5xVp30miexZHbRriHvUnojrKt7isXqWRBFQQNF2w3aYCPUl8/EREWzxtuE+pVI/wbkSGp0a51Nyg1F+L5/nel56xXgt+zcMgeC0FK27gdTzVoPXtI9DBuO2tRhJj94m3/A1GiDZXoM3d5AAAAAElFTkSuQmCC)GitHub +1

2. Formatar (Apagar/Flash) o CYD

O processo de "formatação" no ESP32 é apagar a memória flash para instalar o novo firmware. 

1. Abra o Thonny IDE.
2. Conecte o seu CYD ao computador via USB.
3. No canto inferior direito do Thonny, clique na versão do Python (ex: "Python 3.x.x") e selecione **"Configurar interpretador..."**.
4. Selecione a opção **MicroPython (ESP32)**.
5. Clique no link **"Instalar ou atualizar MicroPython"**.
6. **Porta:** Selecione a porta COM correspondente ao seu dispositivo (ex: COM3, COM4, ou /dev/ttyUSB0).
7. **Arquivo Firmware:** Clique em "Procurar" (Browse) e selecione o arquivo `.bin` que você baixou.
8. **Opção de Apagar (Crucial):** Marque a opção **"Erase flash before installing"** (Apagar flash antes de instalar).
9. Clique em **Install**.
10. **Dica:** Se a instalação falhar, segure o botão **BOOT** na parte de trás do CYD enquanto o Thonny tenta conectar ("Connecting...").

 **Instalar Bibliotecas do Display (ILI9341 e XPT2046) **
Após o flash, o MicroPython estará rodando, mas a tela não funcionará sem drivers.
1. Com o Thonny conectado ao CYD, vá em **Exibir > Arquivos**.
2. No painel "Dispositivo MicroPython" (lado direito), você precisará salvar os arquivos de driver, geralmente `ili9341.py` e `xpt2046.py` (ou `touch.py`).
3. Você pode baixar esses arquivos de repositórios comunitários, como o [JettIsOnTheNet](https://github.com/JettIsOnTheNet/Micropython-Examples-for-ESP32-Cheap-Yellow-Display).
4. Abra cada arquivo no Thonny e vá em **Arquivo > Salvar como... > Dispositivo MicroPython** com o nome corret