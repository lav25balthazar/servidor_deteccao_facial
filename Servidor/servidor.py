import socket
import numpy as np
import cv2
import os

class Servidor():
    """
    Classe Servidor - API Socket
    """

    def __init__(self, host, port):
        """
        Construtor da classe servidor
        """
        self._host = host
        self._port = port
        self.__tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # aqui define qual  protocolo usado (sock_stream), nesse caso tcp


    def start(self):
        """
        Método que inicializa a execução do servidor
        """
        endpoint = (self._host, self._port)
        try:
            self.__tcp.bind(endpoint)
            self.__tcp.listen(1)
            print("Servidor iniciado em ", self._host, ": ", self._port)
            while True:
                con, client = self.__tcp.accept()
                self._service(con, client)
        except Exception as e:
            print("Erro ao inicializar o servidor", e.args)

    def _service(self, con, client):
        """
        Método que implementa o serviço de calculadora
        :param con: objeto socket utilizado para enviar e receber dados
        :param client: é o endereço do cliente
        """
        print("Atendendo cliente ", client)
        while True:
            try:
                tam_bytes = con.recv(4)  # recebe tamanho da imagem
                tam = int.from_bytes(tam_bytes, 'big') # decodifica o tamanho para leitura correta dos bytes da imagem
                img_bytes = con.recv(tam) # recebe imagem

                # decodifica a imagem
                img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

                 # processamento
                xml_classificador = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
                face_cascade = cv2.CascadeClassifier(xml_classificador)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                # # Desenha retângulos nas áreas onde as faces foram detectadas
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

                # codificação para envio da imagem
                _, resp_img_bytes = cv2.imencode('.jpg', img) 
                resp_img_bytes = bytes(resp_img_bytes)
                resp_tamanho = len(resp_img_bytes).to_bytes(4, 'big')

                con.send(resp_tamanho) # ascci -> calculadora, aqui ja foi codificado.
                con.send(resp_img_bytes)

                print(client, " -> requisição atendida")
            except OSError as e:
                print("Erro de conexão ", client, ": ", e.args)
                return
            except Exception as e:
                print("Erro nos dados recebidos pelo cliente ",
                      client, ": ", e.args)
                con.send(bytes("Erro", 'ascii'))
                return