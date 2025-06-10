import streamlit as st
from web3 import Web3
import json
import os
from dotenv import load_dotenv
from streamlit_folium import st_folium
import folium
from geopy.distance import geodesic

load_dotenv()

st.image("ueaest.png", width=170)

st.title("Registro de Presença com Localização")

# Conexão com a blockchain
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER")))
private_key = os.getenv("PRIVATE_KEY")
account = w3.eth.account.from_key(private_key)
w3.eth.default_account = account.address

# ABI e endereço do contrato
with open("abi.json", "r") as f:
    abi = json.load(f)
with open("address.txt", "r") as f:
    contract_address = f.read().strip()
contract = w3.eth.contract(address=contract_address, abi=abi)

# coordenadas uea - -3.0915233948298626, -60.01766405867907
local_autorizado = (-3.1065428592204616, -59.96207255926985) # coordenadas de teste
raio_maximo_metros = 50

st.subheader("Clique no mapa para registrar sua localização atual:")

# Mapa com marcador
mapa = folium.Map(location=local_autorizado, zoom_start=17)
folium.Marker(local_autorizado, tooltip="Local da Aula", icon=folium.Icon(color="green")).add_to(mapa)
map_data = st_folium(mapa, height=350, width=700)

# Lógica de localização
if map_data and map_data["last_clicked"]:
    local_usuario = (
        map_data["last_clicked"]["lat"],
        map_data["last_clicked"]["lng"]
    )
    st.info(f"Você está em: {local_usuario}")
    
    distancia = geodesic(local_autorizado, local_usuario).meters
    st.write(f"Distância até o local autorizado: **{distancia:.2f} metros**")

    if distancia <= raio_maximo_metros:
        st.success("✅ Dentro do raio permitido. Você pode registrar presença.")
        
        aula_atual = contract.functions.aulaAtual().call()
        ja_registrado = contract.functions.verificarPresenca(account.address, aula_atual).call()

        if ja_registrado:
            st.info("✅ Você já registrou presença nesta aula.")
        else:
            if st.button("Registrar presença na blockchain"):
                nonce = w3.eth.get_transaction_count(account.address)
                tx = contract.functions.registrarPresenca().build_transaction({
                    'from': account.address,
                    'nonce': nonce,
                    'gas': 2000000,
                    'gasPrice': w3.to_wei('20', 'gwei')
                })
                signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                st.success(f"Presença registrada! TX: {tx_hash.hex()}")
    else:
        st.error("Você está fora do raio permitido para registrar presença.")
else:
    st.warning("Clique no mapa para capturar sua localização.")

# Botão para o professor iniciar uma nova aula
st.subheader("⚙️ Gerenciamento de Aulas")

if st.button("Iniciar nova aula"):
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.iniciarNovaAula().build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei')
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        st.success(f"Nova aula iniciada com sucesso! TX: {tx_hash.hex()}")
    except Exception as e:
        st.error(f"Erro ao iniciar nova aula: {str(e)}")

# Exibir total de presenças na aula atual
st.divider()
aula_atual = contract.functions.aulaAtual().call()
total_presentes = contract.functions.obterTotalPresentes(aula_atual).call()
st.write(f"🧾 Aula atual: {aula_atual}")
st.write(f"👥 Total de presentes nesta aula: {total_presentes}")
