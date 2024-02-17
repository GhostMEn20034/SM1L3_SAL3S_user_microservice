#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $SQL_USER WITH PASSWORD '$SQL_PASSWORD';
    CREATE DATABASE $SQL_DATABASE;
    GRANT ALL PRIVILEGES ON DATABASE $SQL_DATABASE TO $SQL_USER;
    ALTER DATABASE $SQL_DATABASE OWNER TO $SQL_USER;
EOSQL