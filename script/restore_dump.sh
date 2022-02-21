#!/usr/bin/env bash

if [ -z "$1" ]; then
  echo "restore_dump.sh [path/to/file.dump]"
  exit 1;
fi

echo "===================="
echo "Creating database"
echo "===================="
createdb tetris 2> /dev/null

echo "===================="
echo "Restoring dump"
echo "===================="
psql tetris -f $1

echo "===================="
echo "Applying patches"
echo "===================="
psql tetris -f script/patch_dump.sql
