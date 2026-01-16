#!/bin/bash

mosquitto_pub \
  --host 192.168.2.55 \
  --port 8883 \
  --cafile certs/ca/ca.crt \
  --cert certs/client/test1.crt \
  --key certs/client/test1.key \
  --topic "test/topic" \
  --message "Hallo, MQTT met TLS en clientcertificaat!"
