// mqtt_publisher.js
const mqtt = require('mqtt');
const readline = require('readline');
const fs = require('fs'); // Import the 'fs' module

const MQTT_BROKER_URL = process.env.MQTT_BROKER_URL;
const MQTT_TOPIC = process.env.MQTT_TOPIC || 'modbus/data';

// New environment variables for TLS certificates
const MQTT_CA_CERT = process.env.MQTT_CA_CERT;
const MQTT_CLIENT_KEY = process.env.MQTT_CLIENT_KEY;
const MQTT_CLIENT_CERT = process.env.MQTT_CLIENT_CERT;
const MQTT_TLS_ENABLED = process.env.MQTT_TLS_ENABLED === 'true';

let client;

if (MQTT_TLS_ENABLED && MQTT_CA_CERT && MQTT_CLIENT_KEY && MQTT_CLIENT_CERT) {
  console.log('TLS is enabled. Loading certificates...');
  try {
    const options = {
      protocol: "mqtts",
      host: new URL(MQTT_BROKER_URL).hostname,
      port: 8883, // Standard TLS port
      rejectUnauthorized: false, // For self-signed certificates

      ca: fs.readFileSync(MQTT_CA_CERT),
      key: fs.readFileSync(MQTT_CLIENT_KEY),
      cert: fs.readFileSync(MQTT_CLIENT_CERT),

      clientId: "mqtt-publisher-" + Math.random().toString(16).substr(2, 8),
      clean: true,
      reconnectPeriod: 5000,
    };
    client = mqtt.connect(options);
    console.log(`Connecting to MQTT broker at ${options.host}:${options.port} with TLS...`);
  } catch (error) {
    console.error('Error loading TLS certificates:', error);
    process.exit(1);
  }
} else {
  console.log(`Connecting to MQTT broker at ${MQTT_BROKER_URL} without TLS...`);
  client = mqtt.connect(MQTT_BROKER_URL);
}

client.on('connect', () => {
  console.log('Successfully connected to MQTT broker.');
  console.log(`Will publish messages to topic: ${MQTT_TOPIC}`);
});

client.on('error', (err) => {
  console.error('MQTT connection error:', err);
  process.exit(1);
});

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', (line) => {
  try {
    // We assume the line is a valid JSON string from the python script
    console.log(`Received data: ${line}`);
    client.publish(MQTT_TOPIC, line, (err) => {
      if (err) {
        console.error('Failed to publish message:', err);
      } else {
        console.log(`Published to ${MQTT_TOPIC}`);
      }
    });
  } catch (e) {
    console.error('Could not parse line as JSON:', e);
  }
});

rl.on('close', () => {
    console.log('Input stream closed. Shutting down MQTT client.');
    client.end();
});
