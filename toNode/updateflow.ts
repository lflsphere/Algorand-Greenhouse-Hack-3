// update flow application
import * as algosdk from 'algosdk'
import { OnApplicationComplete } from 'algosdk';

const algodServer = 'http://localhost:4001';
const indexerServer = 'http://localhost:8980';
const token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' ;
const port = '4001';
let  algodclient = new algosdk.Algodv2(algodServer, indexerServer, port );
const  params = await algodclient.getTransactionParams().do();
const minfee=0.000001
let afee= Math.max (minfee,params.fee)
params.fee=afee
let  indexerClient = new algosdk.Indexer(token, indexerServer, port);

let addr ="BTX73BBXFAGATBWZDRUKQRMNDFMR7K7NWETK5CMMJYZK7SVD4JPN2MYZ7I"

const receiver = document.getElementById("receiver").value;
const flowrate = document.getElementById("flowrate").value;
const smartkey = document.getElementById("smartkey").value;

async function updateFlow() { 
    let contractAddress = 123465;
    let note = algosdk.encodeObj({ "contract-call": receiver , flowrate  });
    const app_args = [ note];
    let firstRound = params.lastRound;
    let lastRound = firstRound + 1000;
    console.log(app_args);
    let txn = algosdk.makeApplicationCallTxnFromObject({
        appIndex: contractAddress,
        from: addr,
        onComplete: OnApplicationComplete.NoOpOC,
        suggestedParams: params,
        appArgs: app_args,
       });
  
       let signedTxn = txn.signTxn(smartkey);
       let txId = txn.txID().toString();
       console.log("Signed transaction with txID: %s", txId);
    ;}

  

updateFlow();

