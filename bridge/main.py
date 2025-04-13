import paho.mqtt.client as mqttc
import json
from influxdb_client import InfluxDBClient, Point
import logging
import signal

INFLUXDB_TOKEN = 'aqece41MRt-wGiKkdY7A7n1FPEMAj7ahiZVPD8_TEAKvBHfCPkLxQIf7RoNrG3dGEYECSuSZQZP0GD-Q8bxe0w=='
INFLUXDB_BUCKET = 'home'
INFLUXDB_ORG = 'home'
INFLUXDB_URL = 'http://influxdb:8086'

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    log.info("Subscribed")

def on_connect(client, write_api, connect_flags, reason_code, properties):
    log.info("Connected to broker")
    client.subscribe('environmental/#')

def on_message(client, write_api, message):
    log.info(f"{message.topic} payload={json.loads(message.payload)}")
    topic_components = message.topic.split('/')
    msgdict = json.loads(message.payload)
    point = Point('environmental').tag('devid', topic_components[-1]).field("temp", msgdict['temp']).field("hum", msgdict['hum'])
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

def main():
    write_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = write_client.write_api()

    try:
        client = mqttc.Client(mqttc.CallbackAPIVersion.VERSION2, userdata=write_api)
        client.on_message = on_message
        client.on_connect = on_connect
        client.connect(host='mosquitto')

        def sigint_handler(signum, stack):
            log.info("SIGINT received")
            client.loop_stop()

        signal.signal(signal.SIGINT, sigint_handler)

        client.loop_forever()

    except Exception as e:
        log.exception(f"Exception {repr(e)}")

    except KeyboardInterrupt:
        log.info("Aborted by user")

if __name__ == '__main__':
    logging.basicConfig(style='{', format='{asctime} {name} {levelname} {msg}', level=logging.INFO)
    log = logging.getLogger(__name__)
    main()
