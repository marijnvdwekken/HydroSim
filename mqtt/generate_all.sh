./generate_ca.sh

./generate_server_certs.sh

read -p "Hoeveel clients wil je aanmaken (maximaal 9)?: " n

# validatie: alleen niet-negatieve integers
if ! [[ "$n" =~ ^[0-9]+$ ]]; then
  echo "Fout: voer een positief geheel getal in." >&2
  exit 1
fi

for (( i=1; i<=n; i++ )); do
  ./generate_client_certs.sh
done