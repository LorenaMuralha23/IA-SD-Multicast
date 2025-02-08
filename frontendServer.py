import socket
import struct
import json

from frontend import processRequest


MULTICAST_GROUP = '224.1.1.1'
PORT = 5007

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                1)

sock.bind(('', PORT))

mreq = struct.pack("4s4s", socket.inet_aton(
    MULTICAST_GROUP), socket.inet_aton("0.0.0.0"))
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


def sendToGroup(taskToSend):
    if not taskToSend:  # Verifica se é None ou string vazia
        print("Erro: taskToSend está vazio ou None!")
        return
    sock.sendto(taskToSend.encode(), (MULTICAST_GROUP, PORT))


while True:
    data, addr = sock.recvfrom(4096)
    try:
        decoded_data = data.decode()
        receivedJson = json.loads(decoded_data.strip())  # DICIONARIO

        if (type(receivedJson) is dict):
            if receivedJson.get("machine_id") != "server":
                taskToSend = processRequest(receivedJson)  # dicionario
                sendToGroup(taskToSend)
        else:
            print("Não é um dict")

    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON de {addr}: {data.decode()}")
