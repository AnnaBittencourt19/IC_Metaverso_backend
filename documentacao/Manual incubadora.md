- Parâmetros monitorados por uma incubadora (seria interessante recria-los):
	- Temperatura interna (32–37 °C)
	- Umidade relativa (40–70%)
	- SpO₂ do bebê (≥ 95%)
	- Frequência cardíaca (100–160 bpm)
	- Frequência respiratória (30–60 rpm)
	- CO₂ ambiente (alerta acima de 1000 ppm)
- Estrutura:
```
ESP32 → MQTT Broker → Dashboard ao vivo
```
	- Seria interessante colocar o Display com as informações perto da incubadora também, onde as pessoas que estão monitorando presencialmente também terão acesso as informações que estão sendo transmitidas 

- Precisa de alguns sensores para monitorar os parametros, como:
	- DHT22 para temperatura e umidade
	- MAX30102 para SpO₂ + freq. cardíaca
	- Mq-135 para CO2
