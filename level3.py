mkdir fabric-rest-api
cd fabric-rest-api
npm init -y
npm install express fabric-network body-parser
const express = require('express');
const { Gateway, Wallets } = require('fabric-network');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000;

app.use(express.json());

// Set up Fabric network details
const ccpPath = path.resolve(__dirname, 'connection.json');
const walletPath = path.join(process.cwd(), 'wallet');

// Helper function to connect to the Fabric network
async function connectToNetwork() {
    const gateway = new Gateway();
    const wallet = await Wallets.newFileSystemWallet(walletPath);

    await gateway.connect(ccpPath, {
        wallet,
        identity: 'appUser',
        discovery: { enabled: true, asLocalhost: true },
    });

    const network = await gateway.getNetwork('mychannel');
    const contract = await network.getContract('basic');

    return { gateway, contract };
}

// Create an asset
app.post('/api/assets', async (req, res) => {
    try {
        const { dealerID, msisdn, mpin, balance, status, transAmount, transType, remarks } = req.body;
        const { contract } = await connectToNetwork();
        await contract.submitTransaction('createAsset', dealerID, msisdn, mpin, balance, status, transAmount, transType, remarks);
        res.status(201).send('Asset created');
    } catch (error) {
        res.status(500).send(`Error creating asset: ${error.message}`);
    }
});

// Read an asset
app.get('/api/assets/:dealerID', async (req, res) => {
    try {
        const dealerID = req.params.dealerID;
        const { contract } = await connectToNetwork();
        const result = await contract.evaluateTransaction('readAsset', dealerID);
        res.json(JSON.parse(result.toString()));
    } catch (error) {
        res.status(500).send(`Error reading asset: ${error.message}`);
    }
});

// Update an asset
app.put('/api/assets/:dealerID', async (req, res) => {
    try {
        const dealerID = req.params.dealerID;
        const { balance, status } = req.body;
        const { contract } = await connectToNetwork();
        await contract.submitTransaction('updateAsset', dealerID, balance, status);
        res.send('Asset updated');
    } catch (error) {
        res.status(500).send(`Error updating asset: ${error.message}`);
    }
});

// Get asset history
app.get('/api/assets/:dealerID/history', async (req, res) => {
    try {
        const dealerID = req.params.dealerID;
        const { contract } = await connectToNetwork();
        const result = await contract.evaluateTransaction('getHistoryForAsset', dealerID);
        res.json(JSON.parse(result.toString()));
    } catch (error) {
        res.status(500).send(`Error getting asset history: ${error.message}`);
    }
});

app.listen(port, () => {
    console.log(`REST API server listening on port ${port}`);
});
mkdir wallet
# Use the official Node.js image.
FROM node:14

# Create and set the working directory.
WORKDIR /usr/src/app

# Copy package.json and package-lock.json.
COPY package*.json ./

# Install app dependencies.
RUN npm install

# Copy the rest of the application code.
COPY . .

# Expose the port on which the app will run.
EXPOSE 3000

# Command to run the application.
CMD [ "node", "server.js" ]
docker build -t fabric-rest-api .
docker build -t fabric-rest-api .
docker run -p 3000:3000 -v $(pwd)/wallet:/usr/src/app/wallet -v $(pwd)/connection.json:/usr/src/app/connection.json fabric-rest-api
curl -X POST http://localhost:3000/api/assets -H "Content-Type: application/json" -d '{"dealerID":"dealer123","msisdn":"1234567890","mpin":"1234","balance":"1000","status":"active","transAmount":"50","transType":"credit","remarks":"Initial creation"}'
curl http://localhost:3000/api/assets/dealer123
curl -X PUT http://localhost:3000/api/assets/dealer123 -H "Content-Type: application/json" -d '{"balance":"2000","status":"inactive"}'
curl http://localhost:3000/api/assets/dealer123/history
