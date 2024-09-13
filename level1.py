mkdir -p ~/fabric-dev-servers
cd ~/fabric-dev-servers
curl -sSL https://bit.ly/2ysbOFE | bash -s 2.4.0
cd ~
git clone https://github.com/hyperledger/fabric-samples.git
cd fabric-samples
cd fabric-samples/test-network
./network.sh up createChannel -ca
mkdir -p fabric-samples/asset-transfer-basic/chaincode-javascript
cd fabric-samples/asset-transfer-basic/chaincode-javascript
'use strict';

const { Contract } = require('fabric-contract-api');

class AssetTransferContract extends Contract {

    async createAsset(ctx, dealerID, msisdn, mpin, balance, status, transAmount, transType, remarks) {
        const asset = {
            dealerID,
            msisdn,
            mpin,
            balance: parseInt(balance),
            status,
            transAmount: parseInt(transAmount),
            transType,
            remarks
        };
        await ctx.stub.putState(dealerID, Buffer.from(JSON.stringify(asset)));
    }

    async readAsset(ctx, dealerID) {
        const assetJSON = await ctx.stub.getState(dealerID);
        if (!assetJSON || assetJSON.length === 0) {
            throw new Error(`Asset ${dealerID} does not exist`);
        }
        return JSON.parse(assetJSON.toString());
    }

    async updateAsset(ctx, dealerID, balance, status) {
        const assetJSON = await ctx.stub.getState(dealerID);
        if (!assetJSON || assetJSON.length === 0) {
            throw new Error(`Asset ${dealerID} does not exist`);
        }
        const asset = JSON.parse(assetJSON.toString());
        asset.balance = parseInt(balance);
        asset.status = status;
        await ctx.stub.putState(dealerID, Buffer.from(JSON.stringify(asset)));
    }

    async getHistoryForAsset(ctx, dealerID) {
        const resultsIterator = await ctx.stub.getHistoryForKey(dealerID);
        const results = [];
        while (true) {
            const res = await resultsIterator.next();
            if (res.done) {
                await resultsIterator.close();
                return results;
            }
            if (res.value && res.value.value.toString()) {
                const jsonRes = {
                    TxId: res.value.txId,
                    Timestamp: res.value.timestamp,
                    IsDelete: res.value.isDelete,
                    Value: JSON.parse(res.value.value.toString('utf8'))
                };
                results.push(jsonRes);
            }
        }
    }
}

module.exports = AssetTransferContract;
{
  "name": "asset-transfer-basic",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "fabric-contract-api": "^2.4.0"
  }
}
npm install
cd fabric-samples/test-network
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript -ccl javascript
export PATH=${PWD}/../bin:${PWD}:$PATH
export FABRIC_CFG_PATH=${PWD}/../config
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/tlscacerts/tlsca.org1.example.com-cert.pem
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic -c '{"function":"createAsset","Args":["dealer123","1234567890","1234","1000","active","50","credit","Initial creation"]}'
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic -c '{"function":"updateAsset","Args":["dealer123","2000","inactive"]}'
peer chaincode query -C mychannel -n basic -c '{"Args":["readAsset","dealer123"]}'
peer chaincode query -C mychannel -n basic -c '{"Args":["getHistoryForAsset","dealer123"]}'
