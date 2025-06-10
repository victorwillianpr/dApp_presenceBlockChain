from web3 import Web3
import json
import os
from dotenv import load_dotenv
from solcx import compile_source, install_solc

load_dotenv()
install_solc('0.8.0')

# Conexão com a rede
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER")))

# Chave privada e conta
private_key = os.getenv("PRIVATE_KEY")
account = w3.eth.account.from_key(private_key)
w3.eth.default_account = account.address

# Leitura e compilação do contrato
with open("contrato.sol", "r") as file:
    source_code = file.read()

compiled = compile_source(source_code, solc_version="0.8.0")
contract_id, contract_interface = compiled.popitem()
bytecode = contract_interface["bin"]
abi = contract_interface["abi"]

# Criação do contrato
Contador = w3.eth.contract(abi=abi, bytecode=bytecode)

# Transação de deploy
nonce = w3.eth.get_transaction_count(account.address)
transaction = Contador.constructor().build_transaction({
    'from': account.address,
    'nonce': nonce,
    'gas': 3000000,
    'gasPrice': w3.eth.gas_price,
    'chainId': 11155111  # Sepolia
})

# Assinatura e envio da transação
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Exibe o address de implantação do contrato
print("Contrato implantado em:", tx_receipt.contractAddress)

with open("abi.json", "w") as f:
    json.dump(abi, f)

with open("address.txt", "w") as f:
    f.write(tx_receipt.contractAddress)
