mkdir -p ~/fabric-dev-servers
cd ~/fabric-dev-servers
curl -sSL https://bit.ly/2ysbOFE | bash -s 2.4.0
cd ~
git clone https://github.com/hyperledger/fabric-samples.git
cd fabric-samples
cd fabric-samples/test-network
./network.sh up createChannel -ca
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
cd ../asset-transfer-basic/chaincode-go
type Asset struct
{
    DEALERID    string `json:"dealerid"`
    MSISDN      string `json:"msisdn"`
    MPIN        string `json:"mpin"`
    BALANCE     int    `json:"balance"`
    STATUS      string `json:"status"`
    TRANSAMOUNT int    `json:"transamount"`
    TRANSTYPE   string `json:"transtype"`
    REMARKS     string `json:"remarks"`
}
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
export PATH=${PWD}/../bin:${PWD}:$PATH
export FABRIC_CFG_PATH=${PWD}/../config
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/tlscacerts/tlsca.org1.example.com-cert.pem
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic -c '{"function":"CreateAsset","Args":["asset1","dealer123","1234567890","1234","1000","active","50","credit","Initial transaction"]}'
peer chaincode query -C mychannel -n basic -c '{"Args":["ReadAsset","asset1"]}'
peer chaincode query -C mychannel -n basic -c '{"Args":["GetHistoryForAsset","asset1"]}'

