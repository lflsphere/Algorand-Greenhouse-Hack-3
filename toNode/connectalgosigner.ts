  function check() {
      let checkCodeElem = document.getElementById('check-code');

      if (typeof algorand !== 'undefined') {
        checkCodeElem.innerHTML = 'AlgoSigner is installed.';
      } else {
        checkCodeElem.innerHTML = 'AlgoSigner is NOT installed.';
      }
    }

    function enable() {
      let enableCodeElem = document.getElementById('enable-code');

      algorand.enable({ appName: 'YourAppName' })
      .then((d) => {
        enableCodeElem.innerHTML = JSON.stringify(d, null, 2);
      })
      .catch((e) => {
        console.error(e);
        enableCodeElem.innerHTML = JSON.stringify(e, null, 2);
      })
      .finally(() => {
        hljs.highlightBlock(enableCodeElem);
      });
    }

    function sdkSetup() {
      let sdkSetupCodeElem = document.getElementById('sdk-setup');

      const algodServer = 'https://testnet-algorand.api.purestake.io/ps2';
      const indexerServer = 'https://testnet-algorand.api.purestake.io/idx2';
      const token = { 'X-API-Key': 'B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab' }
      const port = '';

      algodClient = new algosdk.Algodv2(token, algodServer, port);
      indexerClient = new algosdk.Indexer(token, indexerServer, port);

      // Fetch params
      algodClient.getTransactionParams().do()
      .then(d => {
        txnParams = d;
        sdkSetupCodeElem.innerHTML = JSON.stringify(d, null, 2);
      })
      .catch(e => { sdkSetupCodeElem.innerHTML = JSON.stringify(e, null, 2); })
      .finally(() => {
        hljs.highlightBlock(sdkSetupCodeElem);
      });      
    }
    
    function assets(){
      let assetsCodeElem = document.getElementById('assets-code');

      const name = document.getElementById('name').value;
      const limit = document.getElementById('limit').value;

      if (indexerClient === undefined) {
        assetsCodeElem.innerHTML = 'Please run the client setup code first.';
      } else if (!name || !limit) {
        assetsCodeElem.innerHTML = 'Please fill the "name" and "limit" fields.';
      } else {
        indexerClient.searchForAssets()
        .limit(limit)
        .name(name)
        .do()
        .then((d) => {
          assetsCodeElem.innerHTML = JSON.stringify(d, null, 2);
        })
        .catch((e) =>
        console.error(e);
        enableCodeElem.innerHTML = JSON.stringify(e, null, 2);
      });
    } else {
      enableCodeElem.innerHTML = 'AlgoSigner not connected.';
    }
  })
  .catch((e) => {
    console.error(e);
    enableCodeElem.innerHTML = JSON.stringify(e, null, 2);
  })
  .finally(() => {
    hljs.highlightBlock(enableCodeElem);
  });
}
}