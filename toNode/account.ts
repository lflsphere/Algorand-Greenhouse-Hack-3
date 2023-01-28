
// account.ts
import algosdk, { Account, Algodv2 } from algosdk
import { getKmdClient } from './client'

export async function isSandbox(client: Algodv2): Promise<boolean> {
  const params = await client.getTransactionParams().do()

  return params.genesisID === 'devnet-v1' || params.genesisID === 'sandnet-v1'
}

export async function isReachSandbox(client: Algodv2): Promise<boolean> {
  const params = await client.getTransactionParams().do()

  return params.genesisHash === 'lgTq/JY/RNfiTJ6ZcZ/Er8uR775Hk76c7MvHVWjvjCA='
}

export function getAccountFromMnemonic(mnemonic: string): Account {
  return algosdk.mnemonicToSecretKey(mnemonic)
}

export async function getSandboxDefaultAccount(client: Algodv2): Promise<Account> {
  if (!(await isSandbox(client))) {
    throw "Can't get default account from non Sandbox network"
  }

  if (await isReachSandbox(client)) {
    // https://github.com/reach-sh/reach-lang/blob/master/scripts/devnet-algo/algorand_network/FAUCET.mnemonic
    return getAccountFromMnemonic(
      'frown slush talent visual weather bounce evil teach tower view fossil trip sauce express moment sea garbage pave monkey exercise soap lawn army above dynamic'
    )
  }

  const kmd = getKmdClient()
  const wallets = await kmd.listWallets()

  // Sandbox starts with a single wallet called 'unencrypted-default-wallet', with heaps of tokens
  const defaultWalletId = wallets.wallets.filter((w: any) => w.name === 'unencrypted-default-wallet')[0].id

  const defaultWalletHandle = (await kmd.initWalletHandle(defaultWalletId, '')).wallet_handle_token
  const defaultKeyIds = (await kmd.listKeys(defaultWalletHandle)).addresses

  // When you create accounts using goal they get added to this wallet so check for an account that's actually a default account
  let i = 0
  for (i = 0; i < defaultKeyIds.length; i++) {
    const key = defaultKeyIds[i]
    const account = await client.accountInformation(key).do()
    if (account.status !== 'Offline' && account.amount > 1000_000_000) {
      break
    }
  }

  const defaultAccountKey = (await kmd.exportKey(defaultWalletHandle, '', defaultKeyIds[i])).private_key

  const defaultAccountMnemonic = algosdk.secretKeyToMnemonic(defaultAccountKey)
  return getAccountFromMnemonic(defaultAccountMnemonic)
}