#!/bin/bash
# =====================================================
# Script: generate_ca.sh
# Doel:  Genereert een CA private key en rootcertificaat
# =====================================================

# Stop bij fouten
set -e

# Vraag om de Common Name
read -p "Voer de Common Name (CN) in voor de CA (bijv. MyCA): " CN

# Controleer of CN niet leeg is
if [ -z "$CN" ]; then
  echo "Fout: Common Name mag niet leeg zijn."
  exit 1
fi

# Paden (pas eventueel aan)
BASE_DIR="./certs"
CA_DIR="$BASE_DIR/ca"

# Maak de CA directory aan als deze niet bestaat
if [ ! -d "$CA_DIR" ]; then
  echo "CA directory bestaat niet. Maken van $CA_DIR..."
  mkdir -p "$CA_DIR"
fi

# Bestandspaden
CA_KEY="$CA_DIR/ca.key"
CA_CERT="$CA_DIR/ca.crt"

echo "-------------------------------------------"
echo "Genereren van CA private key..."
echo "-------------------------------------------"

openssl genrsa -out "$CA_KEY" 4096

# Stel permissies van de private key in zodat de container het bestand kan lezen
chmod 644 "$CA_KEY"

echo "-------------------------------------------"
echo "Aanmaken van CA rootcertificaat (10 jaar geldig)..."
echo "-------------------------------------------"

openssl req -new -x509 -days 3650 -key "$CA_KEY" -out "$CA_CERT" -subj "/C=NL/O=HHS/CN=${CN}"

echo "-------------------------------------------"
echo "CA certificaat succesvol gegenereerd!"
echo "Bestanden:"
echo "  Private key : $CA_KEY"
echo "  Certificaat : $CA_CERT"
echo "-------------------------------------------"
