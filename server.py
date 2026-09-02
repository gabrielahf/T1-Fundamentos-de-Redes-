
# 1. Criar um socket
# 2. Realizar um bind com a porta especificada
# 3. Iniciar a escuta de requisições de novas conexões
# 4. Estabelecer a conexão
# 5. Realizar a comunicação entre o servidor e o cliente

"""
Servidor de arquivos simples via sockets TCP.
Uso: python3 server.py <ip> <porta>

Protocolo:
  Cliente envia:  "GET <nome-do-arquivo>\n"
  Servidor responde:
    - Sucesso: "OK <tamanho-em-bytes>\n" seguido do conteudo binario do arquivo
    - Erro:    "ERR <mensagem>\n"
"""
import socket
import sys
import os
import threading

CHUNK_SIZE = 65536  # 64 KB por leitura/envio
FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server_files")


def recv_line(conn):
    """Le bytes do socket ate encontrar '\\n' (fim da linha de requisicao).
    TCP e um fluxo de bytes sem 'mensagens', entao lemos byte a byte ate
    achar o delimitador combinado no protocolo."""
    buf = bytearray()
    while True:
        b = conn.recv(1)
        if not b:
            break
        buf += b
        if b == b"\n":
            break
    return bytes(buf)


def handle_client(conn, addr):
    print(f"[+] Conexao de {addr}")
    try:
        request = recv_line(conn).decode("utf-8", errors="replace").strip()
        if not request:
            print(f"[{addr}] requisicao vazia, encerrando")
            return

        parts = request.split(maxsplit=1)
        if len(parts) != 2 or parts[0] != "GET":
            conn.sendall(b"ERR Requisicao invalida. Use: GET <nome-do-arquivo>\n")
            print(f"[{addr}] requisicao invalida: {request!r}")
            return

        filename = parts[1].strip()
        safe_name = os.path.basename(filename)
        filepath = os.path.join(FILES_DIR, safe_name)

        if not os.path.isfile(filepath):
            msg = f"ERR Arquivo nao encontrado: {filename}\n"
            conn.sendall(msg.encode("utf-8"))
            print(f"[{addr}] GET {filename} -> ERR (nao encontrado)")
            return

        filesize = os.path.getsize(filepath)
        conn.sendall(f"OK {filesize}\n".encode("utf-8"))

        sent = 0
        with open(filepath, "rb") as fh:
            while True:
                chunk = fh.read(CHUNK_SIZE)
                if not chunk:
                    break
                conn.sendall(chunk)
                sent += len(chunk)

        print(f"[{addr}] GET {filename} -> OK ({sent} bytes enviados)")

    except (ConnectionResetError, BrokenPipeError) as e:
        print(f"[{addr}] conexao interrompida: {e}")
    except Exception as e:
        print(f"[{addr}] erro inesperado: {e}")
    finally:
        conn.close()
        print(f"[-] Conexao com {addr} encerrada")


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 server.py <ip> <porta>")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    os.makedirs(FILES_DIR, exist_ok=True)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((ip, port))
    server_sock.listen(5)
    print(f"Servidor escutando em {ip}:{port}")
    print(f"Servindo arquivos de: {FILES_DIR}")

    try:
        while True:
            conn, addr = server_sock.accept()
            # thread por conexao -> cada cliente e atendido de forma independente
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        server_sock.close()


if __name__ == "__main__":
    main()
