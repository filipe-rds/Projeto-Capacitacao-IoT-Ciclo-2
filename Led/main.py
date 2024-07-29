import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

# Configuração do LED
LED_PIN = 2  # Pino do LED

# Configuração de conexão ---------------
SSID = "Wokwi-GUEST"
PASSWORD = ""
MQTT_SERVER = "200.129.71.138"
MQTT_USER = "filipe_rodrigues:9748f6"
MQTT_TOPIC = "filipe_rodrigues:9748f6/config"
#---------------------------------------

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

# Função para lidar com mensagens MQTT recebidas
def mqtt_callback(topic, msg):
    try:
        print("Mensagem recebida:", msg)
        msg_str = msg.decode('utf-8')  # Converte a mensagem de bytes para string

        if '1' in msg_str:  # Verifica se '1' está na mensagem
            led.on()
            print("LED ligado")
        elif '0' in msg_str:  # Verifica se '0' está na mensagem
            led.off()
            print("LED desligado")
    except Exception as e:
        print("Erro ao processar a mensagem:", e)

# Função principal
def main():
    try:
        connect_wifi()
        
        # Inicializa o LED
        global led
        led = Pin(LED_PIN, Pin.OUT)
        led.off()  # Garante que o LED comece desligado
        
        # Inicializa o cliente MQTT
        client = MQTTClient("ESP32", MQTT_SERVER, user=MQTT_USER, password="")
        client.set_callback(mqtt_callback)
        client.connect()
        client.subscribe(MQTT_TOPIC)

        print("Aguardando mensagens...")

        while True:
            try:
                client.check_msg()  # Verifica se há mensagens
                time.sleep(1)  # Adiciona um pequeno atraso para evitar sobrecarga da CPU
            except Exception as e:
                print("Erro ao verificar mensagens MQTT:", e)

    except Exception as e:
        print("Erro na execução do programa:", e)
    finally:
        try:
            client.disconnect()
        except:
            print("Erro ao desconectar do MQTT.")

# Executa a função principal
main()
