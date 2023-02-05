const algosdk =require("algosdk");
const readline = require("readline").createInterface({
  input: process.stdin,
  output: process.stdout
});

async function connectWallet() {
  let network = {};

  // Ask the user for the network host
  readline.question("Enter the Algorand network host: ", (host) => {
    network.host = host;

    // Ask the user for the network port
    readline.question("Enter the Algorand network port: ", (port) => {
      network.port = port;

      // Ask the user for the network token
      readline.question("Enter the Algorand network token: ", (token) => {
        network.token = token;
        readline.close();

        // Connect to the Algorand network
        const algodClient = new algosdk.Algodv2(network.token, network.host, network.port);

        // Get the latest block information
        algodClient.block()
          .then(block => {
            console.log("Connected to Algorand network at block: " + block.round);
          })
          .catch(error => {
            console.error("Failed to connect to Algorand network: " + error);
          });
      });
    });
  });
}
export network 
