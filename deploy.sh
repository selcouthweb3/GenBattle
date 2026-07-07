#!/usr/bin/env bash
# GenBattle deployment script — Bradbury testnet
# Usage: ./deploy.sh
# Prerequisites:
#   - genlayer CLI (npx genlayer)
#   - a funded account, unlocked:  npx genlayer account unlock --account <name>

set -e

RPC="https://rpc-bradbury.genlayer.com"
CONTRACT="contracts/fight.py"

echo "Deploying GenBattle to Bradbury testnet..."
npx genlayer deploy \
  --contract "$CONTRACT" \
  --args "Player1" "Player2" \
  --rpc "$RPC"
