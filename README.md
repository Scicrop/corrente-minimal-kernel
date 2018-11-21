![alt text](https://github.com/Compplied/corrente-commons/raw/master/dist/logo.png "Logo Corrente")
# Microkernel Corrente Blockchain

## API

### Nó (node) de registro de informação da Blockchain

#### Criação e carga inical de dados

##### Classe `core.DataNode`

| Argumento | Tipo                                   | Descrição  |
| ----------| -------------------------------------- | ---------- |
| unique_id | inteiro positivo                       | ID único do participante (exemplo: número do pedido) |
| payload   | dicionário do Python (similar ao JSON) | dados do que está sendo representado neste nó (exmeplo: descrição do produto e quantidade) |

##### Exemplo de utilização da API

```python
# importação da classe diretamente do módulo
from corrente import core

# criação do objeto - dados de exemplo, sugestão de uso
node_01 = core.DataNode(unique_id = 1, payload = {'product':'corn','ammount':1500})


##  teste de atributos e métodos
print(node_01.unique_id)
1

print(node_01.payload)
{'product': 'corn', 'ammount': 1500}

print(node_01.hash_chain__object)
None

# teste de exportação para JSON, antes de gerar o hash chain do nó
print(node_01.export_to_json())
{"timestamp": null, "unique_id": 1, "payload": {"product": "corn", "ammount": 1500}, "attachments": [], "extra_hash": null, "hash_chain": null, "signature": null}


## geração do hash chain do nó
node_01.process_hash_chain()

# acesso ao objeto que representa o hash chain
print( node_01.hash_chain__object )
corrente.core.HashObject(b'\x81\r\xb0:\xe1\x89\x9beI\xbb\x81\\\xc4F\xbay\xfa5\x0f,\xb6P\x96\x00\xf1\xf1\xd3T\x89hB[', 'sha256')

# acesso ao hash no formato BASE64
print( node_01.hash_chain__object.base64() )
b'AYENsDrhiZtlSbuBXMRGunn6NQ8stlCWAPHx01SJaEJb'

# acesso ao hash no formato BASE58
print( node_01.hash_chain__object.base58() )
b'Sv653Zb3LxuqLEvUNMxSrUiKGYTp3YM47ZvvbuCXJ4aE'


## geração de assinatura digital do nó
node_01.process_signature()

# acesso à assinatura digital no formato BASE58
print( node_01.signature__object.base58() )
b'NEUcmd7kK5KwbgvvtqkWQQBF8fE8UArRpQmcKzfPmo5e'
```

##### Formatos de serialização do nó

###### Dicionário do Python

Preferível para API interna em Python.

```python
node_01.export_to_python_dict()
```
```python
{'attachments': [],
 'extra_hash': None,
 'hash_chain': b'\x01\x81\r\xb0:\xe1\x89\x9beI\xbb\x81\\\xc4F\xbay\xfa5\x0f,\xb6P\x96\x00\xf1\xf1\xd3T\x89hB[',
 'payload': {'ammount': 1500, 'product': 'corn'},
 'signature': b'\x01;y3\xc9+\xaf\xbd\xdf\xf75\xe9\xee\x88\xee\xb1\xbd\xeeL\xd0\xbe\xa82\x896\x81\x97\xb5 \x13\x87\xa1\xc5',
 'timestamp': '2018-11-16T18:59:37.399346+00:00',
 'unique_id': 1}
```

###### JSON

Preferível para API Web e comunicação inter-processos

```python
node_01.export_to_json()
```
```json
{
    "timestamp": "2018-11-16T18:59:37.399346+00:00",
    "unique_id": 1,
    "payload": {
        "product": "corn",
        "ammount": 1500
    },
    "attachments": [],
    "extra_hash": null,
    "hash_chain": "AYENsDrhiZtlSbuBXMRGunn6NQ8stlCWAPHx01SJaEJb",
    "signature": "ATt5M8krr73f9zXp7ojusb3uTNC+qDKJNoGXtSATh6HF"
}
```

###### Arquivo simples

Preferível para persistência em outras mídias como arquivo de texto (TXT).

```python
node_01.export_to_flat_file()
```
```http
Content-Type: multipart/mixed; boundary="===============5719640193586445364=="
MIME-Version: 1.0

--===============5719640193586445364==
timestamp: 2018-11-16T18:59:37.399346+00:00
hash_chain: 01810DB03AE1899B6549BB815CC446BA79FA350F2CB6509600F1F1D3548968425B


--===============5719640193586445364==
Content-Type: application/octet-stream; description="payload"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit

{
    "product": "corn",
    "ammount": 1500
}
--===============5719640193586445364==--
```

### Nó (node) de regsitro de transação da Blockchain

```python
# todo
```
