import MyAlgoConnect from '@randlabs/myalgo-connect';
import * as algosdk from 'algosdk';
import { OnApplicationComplete } from 'algosdk';
import {FlowEscrow} from '../SC/flow_escrow';
import { encode, decode } from "@msgpack/msgpack";

const algodServer = 'http://localhost:4001';
const indexerServer = 'http://localhost:8980';
const token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' ;
const port = '4001';
const   algodclient = new algosdk.Algodv2(algodServer, indexerServer, port );
const indexerClient = new algosdk.Indexer(token, indexerServer, port);
const myAlgoConnect = new MyAlgoConnect({ disableLedgerNano: false });
const settings = {  shouldSelectOneAccount: false,openManager: false};
const account = await myAlgoConnect.connect(settings);
console.log(account)


async function signer (txn: algosdk.Transaction) 
{let messaget = encode(txn);
    const signedTxn = await myAlgoConnect.signTransaction(txn.toByte());
   return signedTxn;
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
         appIndex: 15634,
         from: account["address"],
         onComplete: OnApplicationComplete.NoOpOC,
         suggestedParams: params,
         appArgs: app_args,
         accounts:["string"]
        });
        
        let signedTxn= await signer(txn);
        let txId = txn.txID().toString();
        console.log("Signed transaction with txID: %s", txId);
            // Submit the transaction
        await algodclient.sendRawTransaction(signedTxn.blob).do();

            // Wait for confirmation
            let confirmedTxn = await algosdk.waitForConfirmation(algodclient, txId, 4);
            //Get the completed Transaction
            console.log("Transaction " + txId + " confirmed in round " + confirmedTxn["confirmed-round"]);
            // let mytxinfo = JSON.stringify(confirmedTxn.txn.txn, undefined, 2);
            // console.log("Transaction information: %o", mytxinfo);
            let string = new TextDecoder().decode(confirmedTxn.txn.txn.note);
            console.log("Note field: ", string);
            let accountInfo = await algodclient.accountInformation(account["address"]).do();
            console.log("Transaction Amount: %d microAlgos", confirmedTxn.txn.txn.amt);        
            console.log("Transaction Fee: %d microAlgos", confirmedTxn.txn.txn.fee);
            console.log("Account balance: %d microAlgos", accountInfo.amount);
           }
        



async function calculateduepayment(address){
    
    const  params = await algodclient.getTransactionParams().do();
    const rtosByte = new TextEncoder().encode("rtos");
    const storByte= new TextEncoder().encode("stor");
    const addressByte=new TextEncoder().encode(account['address']);
    const myreceiversbox=new Uint8Array([...storByte, ...addressByte]);
    const mysendersbox =new Uint8Array([...rtosByte, ...addressByte]);
    const  myreceivers= (await indexerClient.lookupApplicationBoxByIDandName(1234, myreceiversbox).do()).value;
    const mysenders =(await indexerClient.lookupApplicationBoxByIDandName(1234, mysendersbox).do()).value;
    let senderspayment=new Array;
    let receiverspayment= new Array;
    for (let i = 0; i < mysenders.length; i++) {
        console.log(mysenders[i]);
        let mysendersibytes=new TextEncoder().encode('mysenders[i]');
        let addy=new Uint8Array([...mysendersibytes, ...addressByte]);
        let myflow=(await indexerClient.lookupApplicationBoxByIDandName(1234, addy).do()).value;
        let flowraterts=myflow.slice(0, 8);
        let timestampsrts=myflow.slice(8,16);
        let flowratertsnum=parseInt(new TextDecoder().decode(flowraterts));
        let timestampsrtsnum=parseInt(new TextDecoder().decode(timestampsrts));
        let cashcom=flowratertsnum*timestampsrtsnum;
        senderspayment.push(cashcom);} 
    for (let i = 0; i < myreceivers.length; i++) {
            console.log(myreceivers[i]);
            let myreceiversibyte=new TextEncoder().encode('myreceivers[i]');
            let addy=new Uint8Array([...myreceiversibyte, ...addressByte]);
            let myflow=(await indexerClient.lookupApplicationBoxByIDandName(1234,addy ).do()).value;
            let flowraterts=myflow.slice(0, 8);
            let timestampsrts=myflow.slice(8,16);
            let flowratertsnum=parseInt(new TextDecoder().decode(flowraterts));
            let timestampsrtsnum=parseInt(new TextDecoder().decode(timestampsrts));
            let cashout=flowratertsnum*timestampsrtsnum;
            receiverspayment.push(cashout);} 
    return {senderspayment, receiverspayment};   }; 
    async function claim(sender){ let contractAddress = 123465;
        let note = algosdk.encodeObj({ "contract-call":sender });
        const app_args = [note];
        const  params = await algodclient.getTransactionParams().do();
       const minfee=0.001
       let afee= Math.max(minfee,params.fee)
       params.fee=afee
        let firstRound = params.lastRound;
        let lastRound = firstRound + 1000;
        console.log(app_args);
        let txn = algosdk.makeApplicationCallTxnFromObject({
            appIndex: 15634,
            from: account["address"],
            onComplete: OnApplicationComplete.NoOpOC,
            suggestedParams: params,
            appArgs: app_args,
           });
           
           let signedTxn= await signer(txn);
           let txId = txn.txID().toString();
           console.log("Signed transaction with txID: %s", txId);
               // Submit the transaction
           await algodclient.sendRawTransaction(signedTxn.blob).do();
   
               // Wait for confirmation
               let confirmedTxn = await algosdk.waitForConfirmation(algodclient, txId, 4);
               //Get the completed Transaction
               console.log("Transaction " + txId + " confirmed in round " + confirmedTxn["confirmed-round"]);
               // let mytxinfo = JSON.stringify(confirmedTxn.txn.txn, undefined, 2);
               // console.log("Transaction information: %o", mytxinfo);
               let string = new TextDecoder().decode(confirmedTxn.txn.txn.note);
               console.log("Note field: ", string);
               let accountInfo = await algodclient.accountInformation(account["address"]).do();
               console.log("Transaction Amount: %d microAlgos", confirmedTxn.txn.txn.amt);        
               console.log("Transaction Fee: %d microAlgos", confirmedTxn.txn.txn.fee);
               console.log("Account balance: %d microAlgos", accountInfo.amount);
              }

    

