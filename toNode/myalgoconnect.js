import MyAlgoConnect from '@randlabs/myalgo-connect';

const myAlgoConnect = new MyAlgoConnect({ disableLedgerNano: false });

const settings = {
    shouldSelectOneAccount: false,
    openManager: false
};

const accounts = await myAlgoConnect.connect(settings);
console.log(accounts)
export const  addr= accounts["address"];

