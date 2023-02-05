
const algosdk = require("algosdk");
import  network  as network from ./connectwallet.js
const algodclient = new algosdk.Algodv2(network.token, network.host, network.port);

// Replace <CREATE_FLOW_SMART_CONTRACT_ID> with the ID of the create flow smart contract
async function createFlow() {
    async function createFlow() {
        let contractAddress = <CREATE_FLOW_SMART_CONTRACT_ID>;
        let note = new Uint8Array(0);
        let firstRound = (await algodclient.status()).lastRound;
        let lastRound = firstRound + 1000;
        let txn = algosdk.makeContractCallTransaction(<SENDER_ADDRESS>, contractAddress, 0.000001, <FEE>, firstRound, lastRound, note);
        let signedTxn = await algodclient.signTransaction(txn, <SENDER_SK>);
        let tx = (await algodclient.sendRawTransaction(signedTxn.blob));
        console.log("Transaction : " + tx.txId);
        }
        
        createFlow();

