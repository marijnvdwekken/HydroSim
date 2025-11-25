#!/bin/bash
# =====================================================
# Script: generate_client_certs.sh
# Doel:  Genereert een client certificaat + key voor Mosquitto TLS
# =====================================================

# Stop bij fouten
set -e

# Vraag om de Common Name
read -p "Voer de Common Name (CN) in (bijv. client1): " CN

# Controleer of CN niet leeg is
if [ -z "$CN" ]; then
  echo "Fout: Common Name mag niet leeg zijn."
  exit 1
fi

# Paden (pas aan indien nodig)
BASE_DIR="./certs"
CLIENT_DIR="$BASE_DIR/client"
CA_DIR="$BASE_DIR/ca"

# Maak de client directory aan als deze niet bestaat
if [ ! -d "$CLIENT_DIR" ]; then
  echo "Client directory bestaat niet. Maken van $CLIENT_DIR..."
  mkdir -p "$CLIENT_DIR"
fi

# Bestandspaden
KEY_FILE="$CLIENT_DIR/${CN}.key"
CSR_FILE="$CLIENT_DIR/${CN}.csr"
CRT_FILE="$CLIENT_DIR/${CN}.crt"

echo "-------------------------------------------"
echo "Genereren van private key voor client: $CN"
echo "-------------------------------------------"

openssl genrsa -out "$KEY_FILE" 4096

# Stel permissies van de server key in zodat de container het bestand kan lezen
chmod 644 "$KEY_FILE"

echo "-------------------------------------------"
echo "Aanmaken van CSR..."
echo "-------------------------------------------"

openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" -subj "/C=NL/O=MyOrg/CN=${CN}"

echo "-------------------------------------------"
echo "Ondertekenen met CA..."
echo "-------------------------------------------"

openssl x509 -req -in "$CSR_FILE" \
  -CA "$CA_DIR/ca.crt" \
  -CAkey "$CA_DIR/ca.key" \
  -CAserial "$CA_DIR/ca.srl" \
  -out "$CRT_FILE" \
  -days 365

echo "-------------------------------------------"
echo "Certificaat gegenereerd!"
echo "Bestanden:"
echo "  Private key : $KEY_FILE"
echo "  Certificaat : $CRT_FILE"
echo "  CSR         : $CSR_FILE"
echo "-------------------------------------------"
