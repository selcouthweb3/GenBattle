<template>
  <div class="container">
    <h1>⚔️ GenBattle</h1>
    <div class="wallet-box" v-if="!walletConnected">
      <button @click="connectWallet">Connect MetaMask</button>
      <p class="error" v-if="error">{{ error }}</p>
    </div>
    <div v-if="walletConnected">
      <p class="wallet-info">🟢 Connected: {{ shortAddress }}</p>
      <div class="status-box"><p>{{ battleStatus }}</p></div>
      <div class="setup" v-if="!battleStarted">
        <h2>Start a New Battle</h2>
        <input v-model="player1" placeholder="Enter Player 1 name" />
        <input v-model="player2" placeholder="Enter Player 2 name" />
        <button @click="startBattle" :disabled="loading || !player1 || !player2">
          {{ loading ? 'Starting...' : 'Start Battle' }}
        </button>
      </div>
      <div class="battle" v-if="battleStarted && !winner">
        <h2>⚔️ Attack</h2>
        <p>Current Turn: <strong>{{ currentTurn }}</strong></p>
        <input v-model="move" placeholder="Enter your move (e.g. Thunder Punch)" />
        <button @click="attack" :disabled="loading || !move">
          {{ loading ? 'Attacking...' : 'Attack!' }}
        </button>
      </div>
      <div class="winner-box" v-if="winner">
        <h2>🏆 {{ winner }} Wins!</h2>
        <button @click="resetBattle">Play Again</button>
      </div>
      <div class="log" v-if="battleLog.length">
        <h2>Battle Log</h2>
        <ul><li v-for="(entry, index) in battleLog" :key="index">{{ entry }}</li></ul>
      </div>
      <p class="error" v-if="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { createClient } from 'genlayer-js'
import { testnetBradbury } from 'genlayer-js/chains'
import { TransactionStatus } from 'genlayer-js/types'
import { custom } from 'viem'

const CONTRACT_ADDRESS = '0xad34c6d277E9F2aDB169b7cD0B22b6Ce331F87cB' as `0x${string}`

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
const walletConnected = ref(false)
const walletAddress = ref('')

const shortAddress = computed(() =>
  walletAddress.value
    ? walletAddress.value.slice(0, 6) + '...' + walletAddress.value.slice(-4)
    : ''
)

let client: any = null

const getProvider = () => {
  const eth = (window as any).ethereum
  if (!eth) return null
  if (eth.providers?.length) {
    return eth.providers.find((p: any) => p.isMetaMask) ?? eth.providers[0]
  }
  return eth
}

async function connectWallet() {
  try {
    error.value = ''
    const provider = getProvider()
    if (!provider) { error.value = 'MetaMask not found.'; return }

    const accounts = await provider.request({ method: 'eth_requestAccounts' })
    walletAddress.value = accounts[0]

    try {
      await provider.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x' + testnetBradbury.id.toString(16) }]
      })
    } catch (se: any) {
      if (se.code === 4902) {
        await provider.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId: '0x' + testnetBradbury.id.toString(16),
            chainName: testnetBradbury.name,
            rpcUrls: [testnetBradbury.rpcUrls.default.http[0]],
            nativeCurrency: testnetBradbury.nativeCurrency
          }]
        })
      }
    }

    // Create client with MetaMask as the transport so eth_sendTransaction goes through MetaMask
    client = createClient({
      chain: testnetBradbury,
      transport: custom(provider),
      account: walletAddress.value as `0x${string}`,
    })

    walletConnected.value = true
    try { await fetchStatus() } catch (_) { battleStatus.value = 'No active battle' }
  } catch (e: any) {
    error.value = e.message
  }
}

async function sendTx(functionName: string, args: any[]) {
  const txHash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName,
    args,
  })
  await client.waitForTransactionReceipt({
    hash: txHash,
    status: TransactionStatus.ACCEPTED,
    retries: 120,
    interval: 5000,
  })
}

async function startBattle() {
  try {
    loading.value = true
    error.value = ''
    await sendTx('reset_battle', [player1.value, player2.value])
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
    await sendTx('attack', [currentTurn.value, move.value])
    move.value = ''
    await fetchStatus()
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function fetchStatus() {
  const status = await client.readContract({
    address: CONTRACT_ADDRESS,
    functionName: 'get_battle_status',
    args: []
  })
  battleStatus.value = status as string
  const log = await client.readContract({
    address: CONTRACT_ADDRESS,
    functionName: 'get_battle_log',
    args: []
  })
  battleLog.value = (log as string).split(' | ').filter(Boolean)
  if ((status as string).includes('Winner')) {
    winner.value = (status as string).split('Winner: ')[1]
    battleStarted.value = true
  } else if ((status as string).includes('Current Turn')) {
    const parts = (status as string).split('Current Turn: ')
    if (parts[1]) currentTurn.value = parts[1]
    battleStarted.value = true
  }
}

async function resetBattle() {
  battleStarted.value = false
  winner.value = ''
  battleStatus.value = 'No active battle'
  battleLog.value = []
  player1.value = ''
  player2.value = ''
  currentTurn.value = ''
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
button:disabled { background: #555; cursor: not-allowed; }
.wallet-box { text-align: center; padding: 40px 20px; background: #1e1e2e; border-radius: 8px; margin-bottom: 20px; }
.wallet-info { font-size: 0.85rem; color: #2ed573; margin-bottom: 15px; }
.status-box { background: #1e1e2e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
.winner-box { text-align: center; padding: 20px; background: #1e1e2e; border-radius: 8px; margin-bottom: 20px; }
.log { background: #1e1e2e; padding: 15px; border-radius: 8px; margin-top: 20px; }
.log ul { list-style: none; padding: 0; }
.log li { padding: 5px 0; border-bottom: 1px solid #2e2e3e; font-size: 0.9rem; color: #a4b0be; }
.error { color: #ff4757; margin-top: 10px; }
.setup, .battle { background: #1e1e2e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
</style>
