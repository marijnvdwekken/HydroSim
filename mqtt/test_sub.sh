#!/bin/bash

mosquitto_sub \
  --host 192.168.2.55 \
  --port 8883 \
  --cafile certs/ca/ca.crt \
  --cert certs/client/test2.crt \
  --key certs/client/test2.key \
  --topic "test/topic" \
  --verbose
