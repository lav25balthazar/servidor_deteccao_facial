import os
import socket
import cv2
import numpy as np

class Cliente():
    """
    Classe Cliente - API Socket
    """
    def __init__(self, server_ip, port):
        """
        Construtor da classe Cliente
        """
        self.__server_ip = server_ip
        self.__port = port
        self.__tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # aqui define qual  protocolo usado (sock_stream: camada de transporte), nesse caso tcp. tcp: quando o elo é crado, há garantia do recebimento
                                                                       # há uma maior banda por causa do controle, já que quem recebe a nformação diz ok ou nao e, caso nao, o remetentetenta enviar novamente.
                                                                       # no caso do udp não tem essa garantia, o remetente envia a mensagem e não tem certeza se o destinatario a recebeu

    
    def start(self):
        """
        Método que inicializa a execução do Cliente
        """
        endpoint = (self.__server_ip,self.__port) # exemplo de endpoint: 192.168.0.10:900, que é o ip e a porta
        try:
            self.__tcp.connect(endpoint)
            print("Conexão realizada com sucesso!")
            self.__method()  # pede pro usuario dgitar a a operação, codifica e envia
        except:
            print("Servidor não disponível")

    
    def __method(self):
        """
        Método que implementa as requisições do cliente
        """
        try:

            while True:
                num_imagem = input("Digite qual imagem para enviar (1, 2, 3 ou 4 e digite x para sair): ")

                if num_imagem == '':
                    continue
                if num_imagem == 'x':
                    break
                
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                caminho_imagem = os.path.join(base_dir, 'faces', f'image_000{num_imagem}.jpg')
                if not os.path.exists(caminho_imagem):
                    print("Arquivo de imagem não encontrado:", caminho_imagem)
                    continue

                # leitura da imagem
                img_cliente = cv2.imread(caminho_imagem)

                # codificação para bytes
                _, img_bytes = cv2.imencode('.jpg', img_cliente) 
                img_bytes = bytes(img_bytes)
                tamanho_da_imagem_codificado = len(img_bytes).to_bytes(4, 'big')

                # enviar mensagem 
                self.__tcp.send(tamanho_da_imagem_codificado)
                self.__tcp.send(img_bytes)

                
                # espera a resposta
                resp_tamanho = self.__tcp.recv(4) # o tamanho tem 4 bytes
                tam = int.from_bytes(resp_tamanho, 'big') # decofica o tamanho para receber bytes da imagem
                resp_img = self.__tcp.recv(tam)

                # decodifica imagem
                img = cv2.imdecode(np.frombuffer(resp_img, np.uint8), cv2.IMREAD_COLOR)

                cv2.imshow('Imagem Processada', img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            self.__tcp.close()
        except Exception as e:
            print("Erro ao realizar comunicação com o servidor", e.args)
