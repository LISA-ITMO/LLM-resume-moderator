#!/bin/bash

export $(grep -v '^#' .env | xargs)

PGPASSWORD="$PG_PASSWORD" pg_restore -U "$PG_USER" -d "$PG_DATABASE" -h "$PG_HOST" -p "$PG_PORT" data/resume_3.sql
