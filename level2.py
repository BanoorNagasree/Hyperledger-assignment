cd ~
git clone https://github.com/hyperledger/fabric-samples.git
cd fabric-samples
mkdir -p ~/fabric-dev-servers
cd ~/fabric-dev-servers
curl -sSL https://bit.ly/2ysbOFE | bash -s 2.4.0
cd fabric-samples/asset-transfer-basic/chaincode-go
package main

import (
    "encoding/json"
    "fmt"
    "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type Asset struct {
    DEALERID    string `json:"dealerid"`
    MSISDN      string `json:"msisdn"`
    MPIN        string `json:"mpin"`
    BALANCE     int    `json:"balance"`
    STATUS      string `json:"status"`
    TRANSAMOUNT int    `json:"transamount"`
    TRANSTYPE   string `json:"transtype"`
    REMARKS     string `json:"remarks"`
}

type SmartContract struct {
    contractapi.Contract
}

func (s *SmartContract) CreateAsset(ctx contractapi.TransactionContextInterface, dealerID string, msisdn string, mpin string, balance int, status string, transAmount int, transType string, remarks string) error {
    asset := Asset{
        DEALERID:    dealerID,
        MSISDN:      msisdn,
        MPIN:        mpin,
        BALANCE:     balance,
        STATUS:      status,
        TRANSAMOUNT: transAmount,
        TRANSTYPE:   transType,
        REMARKS:     remarks,
    }

    assetJSON, err := json.Marshal(asset)
    if err != nil {
        return fmt.Errorf("failed to marshal asset: %v", err)
    }

    return ctx.GetStub().PutState(dealerID, assetJSON)
}

func (s *SmartContract) ReadAsset(ctx contractapi.TransactionContextInterface, dealerID string) (*Asset, error) {
    assetJSON, err := ctx.GetStub().GetState(dealerID)
    if err != nil {
        return nil, fmt.Errorf("failed to read from world state: %v", err)
    }
    if assetJSON == nil {
        return nil, fmt.Errorf("asset %s does not exist", dealerID)
    }

    var asset Asset
    err = json.Unmarshal(assetJSON, &asset)
    if err != nil {
        return nil, fmt.Errorf("failed to unmarshal asset: %v", err)
    }

    return &asset, nil
}

func (s *SmartContract) UpdateAsset(ctx contractapi.TransactionContextInterface, dealerID string, balance int, status string) error {
    asset, err := s.ReadAsset(ctx, dealerID)
    if err != nil {
        return err
    }

    asset.BALANCE = balance
    asset.STATUS = status

    assetJSON, err := json.Marshal(asset)
    if err != nil {
        return fmt.Errorf("failed to marshal asset: %v", err)
    }

    return ctx.GetStub().PutState(dealerID, assetJSON)
}

func (s *SmartContract) GetHistoryForAsset(ctx contractapi.TransactionContextInterface, dealerID string) ([]QueryResult, error) {
    resultsIterator, err := ctx.GetStub().GetHistoryForKey(dealerID)
    if err != nil {
        return nil, fmt.Errorf("failed to get asset history: %v", err)
    }
    defer resultsIterator.Close()

    var results []QueryResult
    for resultsIterator.HasNext() {
        response, err := resultsIterator.Next()
        if err != nil {
            return nil, fmt.Errorf("failed to iterate results: %v", err)
        }

        results = append(results, QueryResult{TxId: response.TxId, Timestamp: response.Timestamp, IsDelete: response.IsDelete, Value: response.Value})
    }

    return results, nil
}

type QueryResult struct {
    TxId      string `json:"txId"`
    Timestamp string `json:"timestamp"`
    IsDelete  bool   `json:"isDelete"`
    Value     []byte `json:"value"`
}

func main() {
    chaincode, err := contractapi.NewChaincode(new(SmartContract))
    if err != nil {
        fmt.Printf("Error creating asset-transfer-basic chaincode: %s", err.Error())
        return
    }

    if err := chaincode.Start(); err != nil {
        fmt.Printf("Error starting asset-transfer-basic chaincode: %s", err.Error())
    }
}
cd fabric-samples/test-network
./network.sh up createChannel -ca
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
export PATH=${PWD}/../bin:${PWD}:$PATH
export FABRIC_CFG_PATH=${PWD}/../config
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/tlscacerts/tlsca.org1.example.com-cert.pem
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic -c '{"function":"CreateAsset","Args":["dealer123","1234567890","1234","1000","active","50","credit","Initial creation"]}'
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic -c '{"function":"UpdateAsset","Args":["dealer123","2000","inactive"]}'
peer chaincode query -C mychannel -n basic -c '{"Args":["ReadAsset","dealer123"]}'
peer chaincode query -C mychannel -n basic -c '{"Args":["ReadAsset","dealer123"]}'
