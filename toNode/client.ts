
// client.ts
import {Kmd} from 'algosdk'

// KMD client allows you to export private keys, which is useful to get the default account in a sandbox network
export function getKmdClient(): Kmd {
  // We can only use Kmd on the Sandbox otherwise it's not exposed so this makes some assumptions (e.g. same token and server as algod and port 4002)
  return new Kmd(process.env.ALGOD_TOKEN!, process.env.ALGOD_SERVER!, '4001')
}