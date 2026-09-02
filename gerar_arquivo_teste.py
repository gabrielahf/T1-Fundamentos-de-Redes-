"""
Gera um arquivo de teste com tamanho especificado (em MB), util para testar
a transferencia de arquivos grandes.
Uso: python3 gerar_arquivo_teste.py <caminho_saida> <tamanho_mb>
"""
import sys
import os


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 gerar_arquivo_teste.py <caminho_saida> <tamanho_mb>")
        sys.exit(1)

    out_path = sys.argv[1]
    size_mb = int(sys.argv[2])

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    chunk = os.urandom(1024 * 1024)  # 1 MB de dados aleatorios, reaproveitado
    with open(out_path, "wb") as f:
        for _ in range(size_mb):
            f.write(chunk)

    print(f"Arquivo de teste criado: {out_path} ({size_mb} MB)")


if __name__ == "__main__":
    main()
