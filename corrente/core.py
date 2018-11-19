import json
import base64
import hashlib
from datetime import datetime, timezone
from email.message import EmailMessage
from email.encoders import encode_7or8bit
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict, Tuple, List

# import base32_crockford
import base58

# datetime.utcnow().isoformat(timespec='microseconds')

HASH_NULL = b"\xe3\xb0\xc4B\x98\xfc\x1c\x14\x9a\xfb\xf4\xc8\x99o\xb9$'\xaeA\xe4d\x9b\x93L\xa4\x95\x99\x1bxR\xb8U"

class HashObject:
    hash_table = { # :-P
        'sha256': b'\x01',
    }
    def __init__(self, hash_data: bytes, hash_name: str = 'sha256'):
        self.hash_data = hash_data
        self.hash_name = hash_name
    
    def make_playload(self):
        '''Versioned and serialized (bytes) format'''
        prefix = self.hash_table[self.hash_name]
        return prefix + self.hash_data
    
    def base16(self):
        '''Base16 encoding of the versioned and serialized format'''
        return base64.b16encode(self.make_playload())
    
    def base32(self):
        '''Base32 encoding of the versioned and serialized format'''
        return base64.b32encode(self.make_playload())
    
    def base58(self):
        '''Base58 encoding of the versioned and serialized format'''
        return base58.b58encode(self.make_playload())
    
    def base64(self):
        '''Base64 encoding of the versioned and serialized format'''
        return base64.b64encode(self.make_playload())
    
    def base85(self):
        '''Base64 encoding of the versioned and serialized format'''
        return base64.b85encode(self.make_playload())
    
    def __repr__(self):
        return 'corrente.core.HashObject({!r}, {!r})'.format(self.hash_data, self.hash_name)


class DataObject:
    def __init__(self, data: Dict, salt: bytes = b''):
        self.data = data # dict to be converted to a minimal json
        self.salt = salt # bytes to be joined to serialized data before hashing
    
    def serialize(self):
        return self.data # bytes
    
    def hash(self):
        return HashObject(
            hashlib.sha256(
                self.serialize() + self.salt
            ).digest(),
            hash_name='sha256',
        )

class StringObject(DataObject):
    def serialize(self):
        return self.data.strip().encode('utf-8')

class IntegerObject(DataObject):
    def serialize(self):
        return ('{:0d}'.format(self.data)).encode('ascii')

class TimeDateObject(DataObject):
    def serialize(self):
        return self.data.isoformat(timespec='microseconds').encode('ascii')

class JsonObject(DataObject):
    def serialize(self):
        return json.dumps(
            self.data,
            ensure_ascii = False,
            allow_nan = False,
            indent = None,
            separators = (',', ':'),
            sort_keys = True,
        ).encode('utf-8')



class Node():
    pass


class DataNode(Node):
    def __init__(self,
            unique_id: int,
            payload: Dict,
            attachments: List = None,
            extra_hash: bytes = None
        ):
        # data
        self.unique_id = unique_id
        self.payload = payload
        self.attachments = attachments or []
        self.extra_hash = extra_hash
        # processed data
        self.timestamp = None
        self.hash_chain__object = None
        self.signature__object = None
    
    def process_hash_chain(self):
        utc_now = datetime.now(timezone.utc)
        timestamp = TimeDateObject(utc_now).hash().make_playload()
        unique_id = IntegerObject(self.unique_id).hash().make_playload()
        payload = JsonObject(self.unique_id).hash().make_playload()
        if self.attachments:
            raise NotImplemented() # hash chain in order
        else:
            attachments = HASH_NULL
        if self.extra_hash:
            extra_hash = self.extra_hash # validate?
        else:
            extra_hash = HASH_NULL
        
        hash_set = (timestamp, unique_id, payload, attachments, extra_hash)
        hash_joined = b''.join(hash_set)
        
        data_object = DataObject(hash_joined)
        hash_chain__object = data_object.hash()
        
        self.timestamp = utc_now
        self.hash_chain__object = hash_chain__object
        return hash_chain__object
    
    def process_signature(self, method: str = 'sha256'): # TODO: private_key
        assert self.timestamp
        assert not self.signature__object
        timestamp = TimeDateObject(self.timestamp).serialize()
        unique_id = IntegerObject(self.unique_id).serialize()
        payload = JsonObject(self.unique_id).serialize()
        if self.attachments:
            raise NotImplemented() # hash chain in order
        else:
            attachments = b''
        if self.extra_hash:
            extra_hash = self.extra_hash # validate?
        else:
            extra_hash = b''
        
        hash_set = (timestamp, unique_id, payload, attachments, extra_hash)
        bytes_joined = b''.join(hash_set)
        
        data_object = DataObject(bytes_joined)
        self.signature__object = data_object.hash()
        
        return self.signature__object
    
    def export_to_python_dict(self, to_json: bool = False):
        if self.timestamp:
            timestamp = self.timestamp.isoformat(timespec='microseconds')
        else:
            timestamp = None
        
        if self.hash_chain__object:
            if to_json:
                hash_chain = self.hash_chain__object.base64().decode('ascii')
            else:
                hash_chain = self.hash_chain__object.make_playload()
        else:
            hash_chain = None
            
        if self.signature__object:
            if to_json:
                signature = self.signature__object.base64().decode('ascii')
            else:
                signature = self.signature__object.make_playload()
        else:
            signature = None
        
        return {
            'timestamp':   timestamp,
            'unique_id':   self.unique_id,
            'payload':     self.payload,
            'attachments': self.attachments,
            'extra_hash':  self.extra_hash,
            'hash_chain':  hash_chain,
            'signature':   signature,
        }
    
    def export_to_json(self, indent = 4):
        return json.dumps(
            self.export_to_python_dict(to_json=True),
            indent = indent,
        )
    
    def export_to_flat_file(self):
        msg = EmailMessage()
        # timestamp
        if self.timestamp:
            timestamp = self.timestamp.isoformat(timespec='microseconds')
        else:
            timestamp = None
        msg['timestamp'] = timestamp
        # hash_chain
        if self.hash_chain__object:
            hash_chain = self.hash_chain__object.base16().decode('ascii')
        else:
            hash_chain = None
        msg['hash_chain'] = hash_chain
        # json payload and attachments
        mult = MIMEMultipart()
        mult.attach(msg)
        # payload
        payload = json.dumps(self.payload, indent=4)
        mult.attach(MIMEApplication(payload, _encoder=encode_7or8bit, description='payload'))
        # attachments
        for attachment in self.attachments:
            mult.attach(MIMEApplication(attachment, _encoder=encode_7or8bit, description='attachment'))
        #
        # return as bytes
        return mult.as_bytes()


class TransactionNode(Node):
    def __init__(self, source_node_hash_chain: bytes, target_node_hash_chain: bytes):
        self.source_node_hash_chain = source_node_hash_chain
        self.target_node_hash_chain = target_node_hash_chain
        # processed data
        self.timestamp = None
        self.source_signature = None
        self.target_signature = None
        self.hash_chain__object = None
    
    def process_source_signature(self, key: bytes = b'', method: str = 'sha256'): # TODO: private_key
        self.source_signature = HASH_NULL
    
    def process_target_signature(self, key: bytes = b'', method: str = 'sha256'): # TODO: private_key
        self.target_signature = HASH_NULL
    
    def process_hash_chain(self):
        utc_now = datetime.now(timezone.utc)
        self.timestamp = utc_now
        timestamp_hash = TimeDateObject(utc_now).hash().make_playload()
        hash_set = (
            timestamp_hash,
            self.source_node_hash_chain,
            self.target_node_hash_chain,
            self.source_signature,
            self.target_signature)
        hash_joined = b''.join(hash_set)
        data_object = DataObject(hash_joined)
        self.hash_chain__object = data_object.hash()
        return self.hash_chain__object
