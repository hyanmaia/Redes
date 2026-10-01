import socket
import threading
import time
import json
import subprocess

PORTA = 9000
BROADCAST_IP = '255.255.255.255' 

def obter_redes_locais():
    redes = []
    try:
        resultado = subprocess.check_output(['ip', '-4', 'route'], text=True)
        for linha in resultado.splitlines():
            if "scope link" in linha:
                partes = linha.split()
                rede = partes[0]
                interface = partes[2]
                if interface not in ['eth0', 'lo']:
                    redes.append(rede)
    except Exception:
        pass
    return redes

def injetar_rota(rede_destino, ip_gateway):
    minhas_redes = obter_redes_locais()
    
    # Ignora a injeção se for uma rede local do próprio roteador
    if rede_destino in minhas_redes:
        return
        
    try:
        # Comando nativo do Linux: ip route replace <rede> via <gateway>
        subprocess.run(['ip', 'route', 'replace', rede_destino, 'via', ip_gateway], 
                       check=True, stderr=subprocess.DEVNULL)
        print(f"[>] Rota instalada no kernel: {rede_destino} via {ip_gateway}")
    except subprocess.CalledProcessError:
        pass

def escutar_vizinhos():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', PORTA))
    
    print(f"[*] Escutando atualizações na porta {PORTA}...")
    
    while True:
        dados, endereco = sock.recvfrom(1024)
        ip_origem = endereco[0]
        mensagem = json.loads(dados.decode('utf-8'))
        
        # Extrai as redes e tenta injetar na tabela de roteamento
        if 'redes_conhecidas' in mensagem:
            for rede in mensagem['redes_conhecidas']:
                injetar_rota(rede, ip_origem)

def anunciar_rotas():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while True:
        minhas_redes = obter_redes_locais()
        meu_estado = {
            "tipo": "HELLO",
            "redes_conhecidas": minhas_redes
        }
        
        mensagem = json.dumps(meu_estado).encode('utf-8')
        try:
            sock.sendto(mensagem, (BROADCAST_IP, PORTA))
        except Exception:
            pass
        time.sleep(5)

if __name__ == "__main__":
    thread_escuta = threading.Thread(target=escutar_vizinhos, daemon=True)
    thread_anuncio = threading.Thread(target=anunciar_rotas, daemon=True)
    
    thread_escuta.start()
    thread_anuncio.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando algoritmo.")
