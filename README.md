# Servidor de Arquivos via Sockets TCP

Servidor de arquivos e cliente em Python 3, usando apenas a biblioteca
padrão (módulo `socket`), sem dependências externas.

## Requisitos

- Python 3.8 ou superior — nenhum pacote adicional precisa ser instalado.

## Estrutura do projeto

```
.
├── server.py                # Servidor de arquivos
├── client.py                 # Cliente
├── gerar_arquivo_teste.py    # Utilitário para gerar arquivos grandes de teste
├── Makefile                   # Atalhos opcionais de execução
├── server_files/              # Arquivos disponibilizados pelo servidor (criada automaticamente)
└── downloads/                  # Arquivos recebidos pelo cliente (criada automaticamente)
```

## Protocolo da aplicação

Requisição do cliente (uma linha de texto terminada em `\n`):
```
GET <nome-do-arquivo>\n
```

Resposta do servidor:

- **Sucesso:**
  ```
  OK <tamanho-em-bytes>\n
  <conteúdo binário do arquivo, exatamente <tamanho-em-bytes> bytes>
  ```
- **Erro** (arquivo não encontrado ou requisição inválida):
  ```
  ERR <mensagem de erro>\n
  ```

O campo `<tamanho-em-bytes>` permite ao cliente saber exatamente quantos
bytes ler do socket, o que resolve dois problemas: (1) suportar arquivos
grandes sem precisar de um delimitador de fim de arquivo, e (2) evitar
qualquer ambiguidade entre o conteúdo de um arquivo e uma mensagem de erro.

## Como executar

### 1. Colocar arquivos para servir

Coloque os arquivos que deseja disponibilizar dentro de `server_files/`
(criada automaticamente na primeira execução do servidor).

Para gerar um arquivo grande de teste (ex.: 50 MB):
```bash
python3 gerar_arquivo_teste.py server_files/arquivo_grande.bin 50
```

### 2. Iniciar o servidor

```bash
python3 server.py <ip> <porta>
```

Exemplo (escutando em todas as interfaces de rede, porta 5000):
```bash
python3 server.py 0.0.0.0 5000
```

### 3. Executar o cliente

```bash
python3 client.py <ip_do_servidor> <porta> <nome-do-arquivo> [nome_arquivo_local]
```

Exemplo:
```bash
python3 client.py 127.0.0.1 5000 arquivo_grande.bin
```

O arquivo recebido é salvo em `downloads/`.

### Usando o Makefile (opcional)

```bash
make server IP=0.0.0.0 PORT=5000
make client IP=127.0.0.1 PORT=5000 FILE=arquivo_grande.bin
make test-file FILE=arquivo_grande.bin SIZE_MB=50
```

## Testando

### Na mesma máquina (localhost)
Use `127.0.0.1` como IP tanto para o servidor quanto para o cliente.

### Entre duas máquinas diferentes
1. Descubra o IP da máquina que vai rodar o servidor:
   - Linux/Mac: `ifconfig` ou `ip addr`
   - Windows: `ipconfig`
2. Inicie o servidor nessa máquina escutando em todas as interfaces:
   `python3 server.py 0.0.0.0 5000`
3. No cliente, use o IP da máquina do servidor:
   `python3 client.py <ip_do_servidor> 5000 <arquivo>`
4. Se a conexão for recusada, verifique o firewall da máquina que roda o
   servidor (ex.: Firewall do Windows) e libere a porta, ou desative-o
   temporariamente apenas para o teste.

## Tratamento de erros

- Arquivo inexistente: o servidor responde `ERR Arquivo nao encontrado: <nome>`.
- Requisição mal formatada: o servidor responde `ERR Requisicao invalida...`.
- O servidor restringe o acesso a arquivos dentro de `server_files/`
  (proteção contra path traversal, ex.: `GET ../../etc/passwd`), usando
  `os.path.basename` sobre o nome recebido.

## Autores

- Gabriela Hoffmann Roxo
- Luan Pacheco Lima
