import MyAlgoConnect from '@randlabs/myalgo-connect';
import * as algosdk from 'algosdk';
import * as Math from 'Math' ;
const algodServer = 'http://localhost:4001';
const indexerServer = 'http://localhost:8980';
const token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' ;
const port = '4001';
let  algodclient = new algosdk.Algodv2(algodServer, indexerServer, port );
let  indexerClient = new algosdk.Indexer(token, indexerServer, port);
async function myalgoconnect(){
    
    
    
    const myAlgoConnect = new MyAlgoConnect({ disableLedgerNano: false });

const settings = {
    shouldSelectOneAccount: false,
    openManager: false
};

const accounts = await myAlgoConnect.connect(settings);
console.log(accounts)


}
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
         from: accounts["address"],
         onComplete: OnApplicationComplete.NoOpOC,
         suggestedParams: params,
         appArgs: app_args,
        });
        let const signedTxn = await myAlgoConnect.signTxns(txns);
        let txId = txn.txID().toString();
        console.log("Signed transaction with txID: %s", txId);}
function calculateduepayment(address){
    
    let receivers=algosdk.makeApplicationCallTxnFromObject({
        appIndex: 145047401,
        from: accounts["address"],
        onComplete: OnApplicationComplete.NoOpOC,
        suggestedParams: params,
        appArgs: nil ,
       });}
    let  senders= algosdk.makeApplicationCallTxnFromObject({
        appIndex: 145047401,
        from: accounts["address"],
        onComplete: OnApplicationComplete.NoOpOC,
        suggestedParams: params,
        appArgs: nil ,
       });}
async function claimflow(receiver,sender) {
    let contractAddress = 123465;
     let note = algosdk.encodeObj({ "contract-call": receiver , sender  });
     const app_args = [ note];
     const  params = await algodclient.getTransactionParams().do();
    const minfee=0.001
	let pay=calculatedpayment(receiver)[sender];
    
    let afee= Math.max(minfee,params.fee)
    params.fee=afee
     let firstRound = params.lastRound;
     let lastRound = firstRound + 1000;
     console.log(app_args);
     let txn = algosdk.makeApplicationCallTxnFromObject({
         appIndex: 145047401,
         from: accounts["address"],
         onComplete: OnApplicationComplete.NoOpOC,
         suggestedParams: params,
         appArgs: app_args,
        });
        let const signedTxn = await myAlgoConnect.signTxns(txns);
        let txId = txn.txID().toString();
        console.log("Signed transaction with txID: %s", txId);
        