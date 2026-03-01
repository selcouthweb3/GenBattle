<template>
  <div class="container">
    <h1>⚔️ GenBattle</h1>
    <div class="status-box">
      <p>{{ battleStatus }}</p>
    </div>

    <div class="setup" v-if="!battleStarted">
      <h2>Start a New Battle</h2>
      <input v-model="player1" placeholder="Enter Player 1 name" />
      <input v-model="player2" placeholder="Enter Player 2 name" />
      <button @click="startBattle">Start Battle</button>
    </div>

    <div class="battle" v-if="battleStarted && !winner">
      <h2>⚔️ Attack</h2>
      <p>Current Turn: <strong>{{ currentTurn }}</strong></p>
      <input v-model="move" placeholder="Enter your move (e.g. Thunder Punch)" />
      <button @click="attack">Attack!</button>
    </div>

    <div class="winner-box" v-if="winner">
      <h2>🏆 {{ winner }} Wins!</h2>
      <button @click="resetBattle">Play Again</button>
    </div>

    <div class="log" v-if="battleLog.length">
      <h2>Battle Log</h2>
      <ul>
        <li v-for="(entry, index) in battleLog" :key="index">{{ entry }}</li>
      </ul>
    </div>

    <p class="error" v-if="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createClient, createAccount } from 'genlayer-js'
import { studionet } from 'genlayer-js/chains'
import { TransactionStatus } from 'genlayer-js/types'

const contractAddress = (import.meta.env.VITE_CONTRACT_ADDRESS ?? '') as '0x${string}'
const account = createAccount()
const client = createClient({ chain: studionet, account })

const player1 = ref('')
const player2 = ref('')
const move = ref('')
const battleStatus = ref('No active battle')
const battleLog = ref<string[]>([])
const currentTurn = ref('')
const winner = ref('')
const battleStarted = ref(false)
const error = ref('')
const loading = ref(false)

async function startBattle() {
  try {
    loading.value = true
    error.value = ''
    const txHash = await client.writeContract({
      address: contractAddress,
      functionName: 'reset_battle',
      args: [player1.value, player2.value],
      value: BigInt(0),
    })
    await client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.ACCEPTED,
    })
    battleStarted.value = true
    currentTurn.value = player1.value
    winner.value = ''
    battleLog.value = []
    await fetchStatus()
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function attack() {
  try {
    loading.value = true
    error.value = ''
    const txHash = await client.writeContract({
      address: contractAddress,
      functionName: 'attack',
      args: [currentTurn.value, move.value],
      value: 0,
    })
    await client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.ACCEPTED,
    })
    move.value = ''
    await fetchStatus()
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function fetchStatus() {
  try {
    const status = await client.readContract({
      address: contractAddress,
      functionName: 'get_battle_status',
      args: [],
    })
    battleStatus.value = status as string

    const log = await client.readContract({
      address: contractAddress,
      functionName: 'get_battle_log',
      args: [],
    })
    battleLog.value = (log as string).split(' | ').filter(Boolean)

    if ((status as string).includes('Winner')) {
      winner.value = (status as string).split('Winner: ')[1]
    } else {
      const parts = (status as string).split('Current Turn: ')
      if (parts[1]) currentTurn.value = parts[1]
    }
  } catch (e: any) {
    error.value = e.message
  }
}

async function resetBattle() {
  battleStarted.value = false
  winner.value = ''
  battleStatus.value = 'No active battle'
  battleLog.value = []
  player1.value = ''
  player2.value = ''
}
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0f0f1a; color: #fff; font-family: 'Segoe UI', sans-serif; }
.container { max-width: 600px; margin: 40px auto; padding: 20px; }
h1 { text-align: center; font-size: 2.5rem; margin-bottom: 20px; color: #ff4757; }
h2 { margin-bottom: 10px; color: #ffa502; }
input { width: 100%; padding: 10px; margin: 8px 0; border-radius: 8px; border: none; background: #1e1e2e; color: #fff; font-size: 1rem; }
button { width: 100%; padding: 12px; margin-top: 10px; border-radius: 8px; border: none; background: #ff4757; color: #fff; font-size: 1rem; cursor: pointer; }
button:hover { background: #ff6b81; }
.status-box { background: #1e1e2e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
.winner-box { text-align: center; padding: 20px; background: #1e1e2e; border-radius: 8px; margin-bottom: 20px; }
.log { background: #1e1e2e; padding: 15px; border-radius: 8px; margin-top: 20px; }
.log ul { list-style: none; padding: 0; }
.log li { padding: 5px 0; border-bottom: 1px solid #2e2e3e; font-size: 0.9rem; color: #a4b0be; }
.error { color: #ff4757; margin-top: 10px; }
.setup, .battle { background: #1e1e2e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
</style>
