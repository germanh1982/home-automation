import paho.mqtt.client as mqttc
import json
from influxdb_client import InfluxDBClient, Point
import logging
import signal
import yaml
from argparse import ArgumentParser
import sys

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    log.info("Subscribed")

def on_connect(client, write_api, connect_flags, reason_code, properties):
    log.info("Connected to broker")
    client.subscribe(cfg['mqtt']['receive_topic'])

def on_message(client, write_api, message):
    log.info(f"{message.topic} payload={json.loads(message.payload)}")
    topic_components = message.topic.split('/')
    msgdict = json.loads(message.payload)
    point = Point(cfg['data']['measurement_name']).tag('devid', topic_components[-1]).field("temp", msgdict['temp']).field("hum", msgdict['hum'])
    write_api.write(bucket=cfg['influxdb']['bucket'], org=cfg['influxdb']['org'], record=point)

def main():
    write_client = InfluxDBClient(
            url=cfg['influxdb']['url'],
            token=cfg['influxdb']['token'],
            org=cfg['influxdb']['org'])
    write_api = write_client.write_api()

    try:
        client = mqttc.Client(
                mqttc.CallbackAPIVersion.VERSION2,
                userdata=write_api)
        client.on_message = on_message
        client.on_connect = on_connect
        client.connect(host=cfg['mqtt']['host'])

        def sigint_handler(signum, stack):
            log.info("SIGINT received")
            client.loop_stop()
            log.debug("MQTT client stopped")
            sys.exit(0)

        signal.signal(signal.SIGINT, sigint_handler)

        client.loop_forever()

    except Exception as e:
        log.exception(f"Exception {repr(e)}")

    except KeyboardInterrupt:
        log.info("Aborted by user")

if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('configfile')
    args = p.parse_args()
    logging.basicConfig(style='{', format='{asctime} {name} {levelname} {msg}', level=logging.INFO)
    log = logging.getLogger(__name__)

    with open(args.configfile) as cfh:
        cfg = yaml.safe_load(cfh.read())

    main()
