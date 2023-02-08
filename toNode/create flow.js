import * as algosdk from 'algosdk';
import { OnApplicationComplete } from 'algosdk';
import addr  from './myalgoconnect.js' ;
import * as Math from 'Math' ;
const algodServer = 'http://localhost:4001';
const indexerServer = 'http://localhost:8980';
const token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' ;
const port = '4001';
let  algodclient = new algosdk.Algodv2(algodServer, indexerServer, port );
let  indexerClient = new algosdk.Indexer(token, indexerServer, port);



// Replace <CREATE_FLOW_SMART_CONTRACT_ID> with the ID of the create flow smart contract
async function createFlow(receiver,flowrate,smartkey) {
       let contractAddress = 123465;
        let note = algosdk.encodeObj({ "contract-call": receiver , flowrate  });
        const app_args = [ note];
        const  params = await algodclient.getTransactionParams().do();
    const minfee=0.001
    let afee= Math.max(minfee,params.fee)
    params.fee=afee
        let firstRound = params.lastRound;
        let lastRound = firstRound + 1000;
        console.log(app_args);
        let txn = algosdk.makeApplicationCallTxnFromObject({
            appIndex: 145047401,
            from: addr,
            onComplete: OnApplicationComplete.NoOpOC,
            suggestedParams: params,
            appArgs: app_args,
           });
           
           let signedTxn = txn.signTxn(smartkey);
           let txId = txn.txID().toString();
           console.log("Signed transaction with txID: %s", txId);}

