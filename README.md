# Trabalho de Sistemas Operacionais: Roteamento Dinâmico

**Vídeo da apresentação:** [COLOQUE O LINK DO VÍDEO AQUI]

## Sobre o Projeto
Repositório com os arquivos do trabalho de Fundamentos de Sistemas Operacionais (Unisinos). O objetivo foi montar um laboratório virtual para testar na prática como protocolos de roteamento (RIP e OSPF) reagem à queda de links físicos, além da implementação de um algoritmo próprio de roteamento operando no user-space.

A topologia foi estruturada em malha (mesh) para garantir múltiplos caminhos possíveis entre os nós e validar a tolerância a falhas da rede.

## Topologia

*   **5 Roteadores (Core):** Rodando FRRouting (FRR)
*   **5 PCs (Acesso):** Rodando Alpine Linux

mermaid
graph TD
    PC1((PC 1)) --- R1{Roteador 1}
    PC2((PC 2)) --- R2{Roteador 2}
    PC3((PC 3)) --- R3{Roteador 3}
    PC4((PC 4)) --- R4{Roteador 4}
    PC5((PC 5)) --- R5{Roteador 5}

    R1 ===|10.0.12.0/30| R2
    R1 ===|10.0.13.0/30| R3
    R1 ===|10.0.51.0/30| R5

    R2 ===|10.0.23.0/30| R3
    R2 ===|10.0.25.0/30| R5

    R3 ===|10.0.34.0/30| R4
    R4 ===|10.0.45.0/30| R5

    Tecnologias e Pré-requisitos
    
O laboratório foi montado e testado nativamente no CachyOS (Linux), mas é compatível com qualquer distribuição recente. É necessário ter instalado:

Docker

Containerlab

Como rodar o laboratório
1. Subindo a infraestrutura:

Bash
sudo containerlab deploy -t topologia.yaml
2. Configurando o OSPF (Automático):
Foi disponibilizado um script que acessa os containers, ativa os daemons do OSPF, injeta as configurações via vtysh e ajusta as rotas dos PCs de acesso.

Bash
chmod +x preparar_video.sh
./preparar_video.sh
3. Testando a queda do link:
Inicie o ping contínuo do PC1 para o PC5:

Bash
docker exec -it clab-ga-roteamento-pc1 ping 192.168.5.10
Em outro terminal, simule o rompimento do cabo derrubando a interface do Roteador 5:

Bash
docker exec -it clab-ga-roteamento-r5 ip link set dev eth2 down
É possível observar o tráfego falhar rapidamente até o OSPF recalcular a rota usando Dijkstra (cerca de 1 segundo) e a conexão ser restabelecida por um caminho alternativo.

4. Rodando o nosso algoritmo (Python):
Para testar o protocolo desenvolvido rodando direto no User-Space, primeiro desative o OSPF ou reinicie o lab limpo. Depois, execute o script Python nos roteadores (ele descobrirá os vizinhos via UDP e injetará as rotas no Kernel do Linux):

Bash
docker exec -it clab-ga-roteamento-r1 python3 roteamento.py
5. Limpando o ambiente:
Para encerrar os processos, destruir os containers e remover as interfaces virtuais da máquina host:

Bash
sudo containerlab destroy -t topologia.yaml

Autor: Hyan Motter Maia
