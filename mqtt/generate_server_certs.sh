#!/bin/bash
# =====================================================
# Script: generate_server_certs.sh
# Doel:  Genereert een server private key + certificaat voor Mosquitto TLS
# =====================================================

# Stop bij fouten
set -e

# Vraag om de Common Name
read -p "Voer de Common Name (CN) in voor de server (bijv. localhost, broker.mijndomein.nl of het IP-adres): " CN

# Controleer of CN niet leeg is
if [ -z "$CN" ]; then
  echo "Fout: Common Name mag niet leeg zijn."
  exit 1
fi

# Paden (pas aan indien nodig)
BASE_DIR="./certs"
SERVER_DIR="$BASE_DIR/server"
CA_DIR="$BASE_DIR/ca"

# Maak de server directory aan als deze niet bestaat
if [ ! -d "$SERVER_DIR" ]; then
  echo "Server directory bestaat niet. Maken van $SERVER_DIR..."
  mkdir -p "$SERVER_DIR"
fi

# Bestandspaden
KEY_FILE="$SERVER_DIR/server.key"
CSR_FILE="$SERVER_DIR/server.csr"
CRT_FILE="$SERVER_DIR/server.crt"

echo "-------------------------------------------"
echo "Genereren van server private key..."
echo "-------------------------------------------"

openssl genrsa -out "$KEY_FILE" 4096

# Stel permissies van de server key in zodat de container het bestand kan lezen
chmod 644 "$KEY_FILE"

echo "-------------------------------------------"
echo "Aanmaken van server CSR..."
echo "-------------------------------------------"

openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" -subj "/C=NL/O=HHS/CN=${CN}"

echo "-------------------------------------------"
echo "Ondertekenen met CA (1 jaar geldig)..."
echo "-------------------------------------------"

openssl x509 -req -in "$CSR_FILE" \
  -CA "$CA_DIR/ca.crt" \
  -CAkey "$CA_DIR/ca.key" \
  -CAcreateserial \
  -out "$CRT_FILE" \
  -days 365

echo "-------------------------------------------"
echo "Server certificaat succesvol gegenereerd!"
echo "Bestanden:"
echo "  Private key : $KEY_FILE"
echo "  Certificaat : $CRT_FILE"
echo "  CSR         : $CSR_FILE"
echo "-------------------------------------------"
