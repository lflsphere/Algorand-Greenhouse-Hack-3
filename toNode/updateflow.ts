// update flow application

const algosdk = require("algosdk");
import  network  as network from ./connectwallet.js
const algodclient = new algosdk.Algodv2(network.token, network.host, network.port);

// Replace <UPDATE_FLOW_SMART_CONTRACT_ID> with the ID of the update flow smart contract
async function updateFlow() {
    let contractAddress = <UPDATE_FLOW_SMART_CONTRACT_ID>;
    let note = new Uint8Array(0);
    let txn = algosdk.makeContractCallTransaction(<SENDER_ADDRESS>, contractAddress, <AMOUNT>, <FEE>, <FIRST_VALID_ROUND>, <LAST_VALID_ROUND>, note);
    let signedTxn = await algodclient.signTransaction(txn, <SENDER_SK>);
    let tx = (await algodclient.sendRawTransaction(signedTxn.blob));
    console.log("Transaction : " + tx.txId);
}

updateFlow();

