# cliente de un servidor UPD en python
import os
import socket
import sys
import threading
import datetime
from time import time
import queue as q

server_address = ('192.168.1.78', 3400)

def recive_data(sock, i, queue, numConnections):

    # Guardar en la carpeta ArchivosRecibidos
    file = open("UDP/ArchivosRecibidos/Cliente" + str(i) + "-Prueba-" + numConnections + ".txt", "w")
    
    # Recibir respuesta
    print(sys.stderr, 'Cliente ' + str(i) + ' - ' + 'Esperando respuesta')

    start_time = time()
    data = b'data'
    while data:
        try:
            sock.settimeout(120)
            data, server = sock.recvfrom(65500)
            if data == b'FIN':
                print(sys.stderr, 'Cliente ' + str(i) + ' - ' + 'Recibido "%s"' % data)
                break
            
            file.write(data.decode())
        except socket.timeout:
            print(sys.stderr, 'Cliente ' + str(i) + ' - ' + 'Tiempo de espera agotado, cerrando socket')
            socket.close()
            break

    print(sys.stderr, 'Cliente ' + str(i) + ' - ' + 'Cerrando socket ' + str(i))
    
    end_time = time()
    total_time = end_time - start_time

    sock.close()

    queue.put(total_time)


if __name__ == "__main__":

    idThread = 0

    init_message = input('Introduce el tamaño del mensaje: ').encode()
    sec_message = input('Introduce el número de clientes: ')

    # Obtener la fecha y hora actual para el nombre del archivo de logs
    actual_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    log = open('UDP/Logs/' + actual_date + '-log.txt', 'w')        
    
    for i in range(0, int(sec_message)):

        # Crear un socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Ajustar el tamaño del buffer de recepción
        buffer_size = 66560
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)

        # Enviar datos
        print(sys.stderr, 'Cliente ' + str(i) + ' - ' + 'Enviando') #  % message
        sent = sock.sendto(init_message, server_address)

        queue = q.Queue()

        thread = threading.Thread(target=recive_data, args=(sock, i, queue, sec_message))
        idThread += 1
        thread.start()

        thread.join()
        total_time = queue.get(block=True)

        # Verificación correctitud del archivo recibido
        filesize = os.path.getsize('UDP/ArchivosRecibidos/Cliente' + str(i) + '-Prueba-' + sec_message + '.txt')
        
        success = 'Error en transferencia (el archivo no se recibió completo)'
        if filesize == int(init_message.decode()) * 1048576:
            success = 'Transferencia exitosa'

        log.write(f'[Cliente {i}], {success} ({filesize} bytes vs {int(init_message.decode()) * 1048576}), Tiempo: {total_time} segundos\n')
