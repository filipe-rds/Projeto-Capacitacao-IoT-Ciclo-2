import network
import time
import ujson
from machine import Pin, ADC
from umqtt.simple import MQTTClient
import math

# Configurações do sensor de temperatura
NTC_PIN = 34  # Pino do sensor NTC
BETA = 3950   # Constante do NTC

# Configuração de conexão ---------------
SSID = "Wokwi-GUEST"
PASSWORD = ""
MQTT_SERVER = "200.129.71.138"
MQTT_USER = "filipe_rodrigues:34ae52"
MQTT_TOPIC = "filipe_rodrigues:34ae52/attrs"
#---------------------------------------

# Inicializa o ADC para leitura do sensor
adc = ADC(Pin(NTC_PIN))

# Função para conectar ao Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    # Tempo máximo de espera para conectar
    max_attempts = 10
    attempts = 0

    while not wlan.isconnected() and attempts < max_attempts:
        time.sleep(0.5)
        print("Conectando ao Wi-Fi...")
        attempts += 1

    if wlan.isconnected():
        print("Conectado ao Wi-Fi:", wlan.ifconfig())
    else:
        print("Falha ao conectar ao Wi-Fi.")
        raise Exception("Falha na conexão Wi-Fi.")

# Função para calcular a temperatura em Celsius
def read_temperature():
    try:
        analog_value = adc.read()
        celsius = 1 / (math.log(1 / (4095.0 / analog_value - 1)) / BETA + 1.0 / 298.15) - 273.15
        return celsius
    except Exception as e:
        print("Erro ao ler a temperatura:", e)
        return None  # Retorna None em caso de erro

# Função para enviar a mensagem via MQTT
def publish_temperature(client):
    temperature = read_temperature()
    if temperature is not None:  # Verifica se a temperatura foi lida corretamente
        message = ujson.dumps({"Temperatura": temperature})
        client.publish(MQTT_TOPIC, message)
        print("Mensagem enviada:", message)
    else:
        print("Temperatura não disponível. Mensagem não enviada.")

# Função principal
def main():
    try:
        connect_wifi()
        
        # Inicializa o cliente MQTT
        client = MQTTClient("ESP32", MQTT_SERVER, user=MQTT_USER, password="")
        client.connect()
        
        try:
            while True:
                publish_temperature(client)
                time.sleep(2)  # Aguarda 2 segundos antes da próxima leitura
        except Exception as e:
            print("Erro durante a publicação da temperatura:", e)
    finally:
        client.disconnect()

# Executa a função principal
main()
