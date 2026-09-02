IP ?= 127.0.0.1
PORT ?= 5000
FILE ?= arquivo_grande.bin
SIZE_MB ?= 50

.PHONY: server client test-file clean

server:
	python3 server.py $(IP) $(PORT)

client:
	python3 client.py $(IP) $(PORT) $(FILE)

test-file:
	python3 gerar_arquivo_teste.py server_files/$(FILE) $(SIZE_MB)

clean:
	rm -rf downloads
