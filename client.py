
# 1. Criar um socket
# 2. Solicitar a conexão
# 3. Realizar a comunicação entre o cliente e o servidor

"""
Cliente de arquivos simples via sockets TCP.
Uso: python3 client.py <ip_servidor> <porta> <nome-do-arquivo> [nome_arquivo_local]
"""
import socket
import sys
import os
import time

CHUNK_SIZE = 65536  # 64 KB por leitura


def recv_line(sock):
    """Le bytes ate encontrar '\\n', delimitador da linha de cabecalho da resposta."""
    buf = bytearray()
    while True:
        b = sock.recv(1)
        if not b:
            break
        buf += b
        if b == b"\n":
            break
    return bytes(buf)


def recv_and_save(sock, n, out_path):
    """Recebe exatamente n bytes do socket, gravando diretamente em disco
    (sem manter o arquivo inteiro em memoria - importante para arquivos grandes).
    Retorna (bytes_recebidos, numero_de_chamadas_recv)."""
    received = 0
    calls = 0
    with open(out_path, "wb") as f:
        while received < n:
            remaining = n - received
            chunk = sock.recv(min(CHUNK_SIZE, remaining))
            calls += 1
            if not chunk:
                raise ConnectionError("Conexao encerrada antes do fim do arquivo")
            f.write(chunk)
            received += len(chunk)
    return received, calls


def main():
    if len(sys.argv) < 4:
        print("Uso: python3 client.py <ip_servidor> <porta> <nome-do-arquivo> [nome_arquivo_local]")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    out_name = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(filename)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
        sock.sendall(f"GET {filename}\n".encode("utf-8"))

        header = recv_line(sock).decode("utf-8", errors="replace").strip()
        if not header:
            print("Servidor encerrou a conexao sem responder.")
            return

        parts = header.split(maxsplit=1)
        status = parts[0] if parts else ""

        if status == "OK":
            filesize = int(parts[1])
            os.makedirs("downloads", exist_ok=True)
            out_path = os.path.join("downloads", out_name)

            print(f"Recebendo '{filename}' ({filesize} bytes)...")
            t0 = time.time()
            received, calls = recv_and_save(sock, filesize, out_path)
            elapsed = time.time() - t0

            print(f"Arquivo salvo em: {out_path}")
            print(f"Total recebido: {received} bytes")
            print(f"Chamadas de recv() necessarias para o corpo: {calls}")
            print(f"Tempo: {elapsed:.3f}s")

        elif status == "ERR":
            msg = parts[1] if len(parts) > 1 else "erro desconhecido"
            print(f"Erro retornado pelo servidor: {msg}")
        else:
            print(f"Resposta inesperada do servidor: {header!r}")

    except ConnectionRefusedError:
        print(f"Nao foi possivel conectar a {ip}:{port}. O servidor esta rodando?")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
