import json
import base64
import hashlib
from datetime import datetime, timezone
from email.message import EmailMessage
from email.encoders import encode_7or8bit
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# import base32_crockford
import base58

# datetime.utcnow().isoformat(timespec='microseconds')

HASH_NULL = b"\xe3\xb0\xc4B\x98\xfc\x1c\x14\x9a\xfb\xf4\xc8\x99o\xb9$'\xaeA\xe4d\x9b\x93L\xa4\x95\x99\x1bxR\xb8U"

class HashObject:
    hash_table = { # :-P
        'sha256': b'\x01',
    }
    def __init__(self, hash_data, hash_name='sha256'):
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
    


class DataObject:
    def __init__(self, data, salt=b''):
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


class Node:
    def __init__(self, unique_id, payload, attachments=None, extra_hash=None):
        # data
        self.unique_id = unique_id
        self.payload = payload
        self.attachments = attachments or []
        self.extra_hash = extra_hash
        # processed data
        self.timestamp = None
        self.hash_chain__object = None
        self.signature = None
    
    def hash_chain(self):
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
    
    def sign_data(self, method='sha256'): # TODO: private_key
        assert self.timestamp
        assert not self.signature
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
        
        self.signature = HashObject(bytes_joined, method)
        return self.signature
    
    def to_dict(self, to_json=False):
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
            
        if self.signature:
            if to_json:
                signature = self.signature.base64().decode('ascii')
            else:
                signature = self.signature.make_playload()
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
    
    def to_json(self):
        return json.dumps(self.to_dict(to_json=True))
    
    def to_flat_file(self):
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
        payload = '{"x":"ç"}'.encode('utf-8')
        mult.attach(MIMEApplication(payload, _encoder=encode_7or8bit, description='payload'))
        # attachments
        for attachment in self.attachments:
            mult.attach(MIMEApplication(attachment, _encoder=encode_7or8bit, description='attachment'))
        #
        # return as bytes
        return mult.as_bytes()
