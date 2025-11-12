#!/bin/bash
# =====================================================
# Script: gen_server_cert.sh
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
BASE_DIR="."
SERVER_DIR="$BASE_DIR/server"
CA_DIR="$BASE_DIR/ca"

# Bestandspaden
KEY_FILE="$SERVER_DIR/${CN}.key"
CSR_FILE="$SERVER_DIR/${CN}.csr"
CRT_FILE="$SERVER_DIR/${CN}.crt"

echo "-------------------------------------------"
echo "Genereren van server private key..."
echo "-------------------------------------------"

openssl genrsa -out "$KEY_FILE" 4096

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
