import os
from web3 import Web3
from solcx import compile_source, install_solc, get_installed_solc_versions, set_solc_version

REQUIRED_SOLC_VERSION = "0.8.0"

# Install solc if missing
if REQUIRED_SOLC_VERSION not in [str(v) for v in get_installed_solc_versions()]:
    print(f"Installing Solidity compiler version {REQUIRED_SOLC_VERSION}...")
    install_solc(REQUIRED_SOLC_VERSION)

set_solc_version(REQUIRED_SOLC_VERSION)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
if not w3.is_connected():
    raise ConnectionError("Cannot connect to local Ethereum node at http://127.0.0.1:7545. Start Ganache or your node.")

default_account = w3.eth.accounts[0]
w3.eth.default_account = default_account

contract_path = os.path.join(os.path.dirname(__file__), "smart_contract", "TenderContract.sol")
with open(contract_path, "r") as f:
    source_code = f.read()

compiled_sol = compile_source(source_code)
contract_interface = compiled_sol['<stdin>:Tender']


def deploy_contract(title):
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    tx_hash = contract.constructor(title).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return contract, tx_hash.hex(), tx_receipt.contractAddress


def load_contract(address):
    return w3.eth.contract(address=address, abi=contract_interface['abi'])
