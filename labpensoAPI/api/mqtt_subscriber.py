import paho.mqtt.client as mqtt
import json
from .models import Weather_Station, Day, Measurement
from django.utils import timezone
import threading
from api.serializers import MeasurementSerializer
from decouple import config

MQTT_BROKER_HOST = config('MQTT_BROKER_HOST')
MQTT_BROKER_PORT = int(config('MQTT_BROKER_PORT'))
MQTT_TOPIC = config('MQTT_TOPIC')
MQTT_PASSWORD = config('MQTT_PASSWORD')
MQTT_USER = config('MQTT_USER')

def on_connect(client, userdata, flags, rc):
    """Callback quando a conexão com o broker MQTT é estabelecida."""
    if rc == 0:
        print("Conectado ao broker MQTT com sucesso!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Falha ao conectar ao broker MQTT, código de retorno {rc}")

def on_message(client, userdata, msg):
    """Callback quando uma mensagem MQTT é recebida."""
    try:
        payload = json.loads(msg.payload.decode())  # Assume payload como JSON
        print(f"Mensagem recebida no tópico {msg.topic}: {payload}")

        # Validação e transformação dos dados
        payload["timestamp"] = payload["timestamp"].replace("Z", "+00:00") 

        # Criar serializer com os dados recebidos
        serializer = MeasurementSerializer(data=payload)

        if serializer.is_valid():
            serializer.save()
            print("Medição salva com sucesso no banco de dados!")
        else:
            print(f"Erro de validação do serializer: {serializer.errors}")

    except json.JSONDecodeError:
        print(f"Erro: Payload da mensagem MQTT não é JSON válido: {msg.payload.decode()}")
    except Exception as e:
        print(f"Erro ao processar mensagem MQTT: {e}")
        
def mqtt_subscribe_loop():
    """Função para configurar o cliente MQTT e iniciar o loop de inscrição."""
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60) # Conectar ao broker
        client.loop_forever() # Loop blocking que mantém a conexão e processa mensagens
    except Exception as e:
        print(f"Erro ao iniciar o cliente MQTT: {e}")


def start_mqtt_subscriber():
    """Inicia o subscriber MQTT em uma thread separada."""
    thread = threading.Thread(target=mqtt_subscribe_loop, daemon=True)
    thread.start()
    print("Subscriber MQTT iniciado em background...")