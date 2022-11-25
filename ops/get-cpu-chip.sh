#!/bin/bash -x
set -e

# Check operating system since sysctl isn't a valid Windows command
# Windows
if [[ "$OSTYPE" == "msys" ]]; then
  echo "intel"
# Mac
elif [[ "$OSTYPE" == "darwin"* ]]; then
  # Grab chip details from system to avoid emulated shell descriptors
  SYS_CHIP=$(sysctl -n machdep.cpu.brand_string)
  
  # Output (can't 'return' like a JS function. Bash expects piping streams)
  if [[ $SYS_CHIP == "Apple M1" ]]
  then
    echo "m1"
  else
    echo "intel"
  fi
else
  echo "Unhandled operating system"
  exit 1
fi
