# Genereer het root-certificaat
./broker/certs/generate_ca.sh

# Genereer de key en het certificaat van de server
./broker/certs/generate_server_certs.sh

# Lees in hoeveel clients er gemaakt moeten worden.
read -p "Hoeveel clients wil je aanmaken (maximaal 9)?: " n

# Validatie: alleen niet-negatieve integers
if ! [[ "$n" =~ ^[0-9]+$ ]]; then
  echo "Fout: voer een positief geheel getal in." >&2
  exit 1
fi

# Maak zoveel clients aan als dat er ingevuld is
for (( i=1; i<=n; i++ )); do
  ./broker/certs/generate_client_certs.sh
done
