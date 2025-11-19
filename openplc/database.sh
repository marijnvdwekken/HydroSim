#!/bin/bash
set -euo pipefail

# modifying openplc database
# https://github.com/thiagoralves/OpenPLC_v3/blob/master/webserver/openplc.db

DB_PATH="/OpenPLC_v3/webserver/openplc.db"

# Reset the OpenPLC program table so the runtime always finds script.st.
sqlite3 "$DB_PATH" <<'SQL'
DELETE FROM Programs;
INSERT INTO Programs (Name, Description, File, Date_upload)
VALUES ('Program Name', 'Desc', 'script.st', strftime('%s', 'now'));
SQL

# remove all existing slave devices
sqlite3 "$DB_PATH" "DELETE FROM Slave_dev"

# Change or disable Modbus port. Comment out if not required.
sqlite3 "$DB_PATH" "UPDATE Settings SET Value = '502' WHERE Key = 'Modbus_port';"

# enable openplc start run mode. Comment out if not required.
sqlite3 "$DB_PATH" "UPDATE Settings SET Value = 'true' WHERE Key = 'Start_run_mode';"
