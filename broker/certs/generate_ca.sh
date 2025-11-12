#!/bin/bash
# =====================================================
# Script: gen_ca_cert.sh
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
BASE_DIR="."
CA_DIR="$BASE_DIR/ca"

# Bestandspaden
CA_KEY="$CA_DIR/ca.key"
CA_CERT="$CA_DIR/ca.crt"

echo "-------------------------------------------"
echo "Genereren van CA private key..."
echo "-------------------------------------------"

openssl genrsa -out "$CA_KEY" 4096

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
