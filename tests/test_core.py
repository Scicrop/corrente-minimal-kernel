import pytest
from datetime import datetime, timezone
from functools import partial

import os.path
import sys
sys.path += [os.path.join(os.path.dirname(__file__), '..')]
print(sys.path)

from freezegun import freeze_time

from corrente import core

private_key = '''-----BEGIN RSA PRIVATE KEY-----
MIIBOgIBAAJBAL4sgsYGcP7iZ5dP5vccw4+y/79bN4UUtJ/0rX53CjidIups0qQI
9GkuuXCHVMzUfDjgHcQsUELDb3rcxbAJLo8CAwEAAQJAUD4ty+rJ4PKdLT58wUY0
yjyIJzERAylSca/nSNZnzKzdGKjzXvV9F6qu/8KJ4xmiGyrmt3aA8NwpQ/+27twF
eQIhAP3EcqElbY6WzZAUYoo1kYs+ckJB0g1jIn6OjY80A/R9AiEAv9jVW2xJnaJj
6gZSKCRhGcJ+ptuhdSOM9kp/DCKL2PsCIQClkHPRW1/9NbpsFECuN4D7vgRB4juv
bExnEY6eLaue6QIgDU97BhvOQ7yXmA4WNyjG/+WJqgQFAL6VsiTbCbl/4G8CIDzZ
dbu2ycF+gwyKu7f+RlV+AU5W90je0qALJJa0AqkT
-----END RSA PRIVATE KEY-----'''

public_key = '''-----BEGIN PUBLIC KEY-----
MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAL4sgsYGcP7iZ5dP5vccw4+y/79bN4UU
tJ/0rX53CjidIups0qQI9GkuuXCHVMzUfDjgHcQsUELDb3rcxbAJLo8CAwEAAQ==
-----END PUBLIC KEY-----'''

def test_data_object():
    d1_dict = {'x': 1, 'y': 2}
    d2_dict = {'y': 2, 'x': 1} # needs Python 3.6.5 or OrderedDicts
    assert d1_dict == d2_dict
    assert list(d1_dict.keys()) != list(d2_dict.keys())
    assert list(d1_dict.keys()) == list(reversed(list(d2_dict.keys())))
    
    d1 = core.JsonObject(data = d1_dict)
    d2 = core.JsonObject(data = d2_dict)
    assert list(d1.data.keys()) != list(d2.data.keys())
    assert d1 is not d2
    
    assert d1.serialize() == d2.serialize()
    assert d1.serialize() == b'{"x":1,"y":2}'
    
    assert len(d1.hash().hash_data) == len(d2.hash().hash_data)
    assert d1.hash().hash_data == d2.hash().hash_data
    assert d1.hash().hash_data == b'h\x9a\x8f\x1d\xb9T\x02X\x04v\xe3\x8c&Bx\xce{\x1efC \xcf\xb4\xe9\xae\x8d:\x90\x8c\xf0\x99d'
    
    assert(d1.hash().make_playload()) == b'\x01h\x9a\x8f\x1d\xb9T\x02X\x04v\xe3\x8c&Bx\xce{\x1efC \xcf\xb4\xe9\xae\x8d:\x90\x8c\xf0\x99d'
    
    assert(d1.hash().base16()) == b'01689A8F1DB95402580476E38C264278CE7B1E664320CFB4E9AE8D3A908CF09964'
    assert(d1.hash().base32()) == b'AFUJVDY5XFKAEWAEO3RYYJSCPDHHWHTGIMQM7NHJV2GTVEEM6CMWI==='
    assert(d1.hash().base58()) == b'RGeTutmqksMoBpKAnR1nrCMT1ARmmbpgKQvaZ55emztb'
    assert(d1.hash().base64()) == b'AWiajx25VAJYBHbjjCZCeM57HmZDIM+06a6NOpCM8Jlk'
    assert(d1.hash().base85()) == b'0ce_!9l2BjSOj+Cj3z>O&U+qaLm<zz>8_1Bkc{w|WB'
    
    d3_salt = b'0\\0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03K\x000H\x02A\x00\xbe,\x82\xc6\x06p\xfe\xe2g\x97O\xe6\xf7\x1c\xc3\x8f\xb2\xff\xbf[7\x85\x14\xb4\x9f\xf4\xad~w\n8\x9d"\xeal\xd2\xa4\x08\xf4i.\xb9p\x87T\xcc\xd4|8\xe0\x1d\xc4,PB\xc3oz\xdc\xc5\xb0\t.\x8f\x02\x03\x01\x00\x01'
    d3 = core.JsonObject(data = d1_dict, salt = d3_salt)
    assert d3.serialize() == d1.serialize()
    
    assert len(d3.hash().hash_data) == len(d1.hash().hash_data)
    assert d3.hash().hash_data != d1.hash().hash_data
    assert d3.hash().hash_data == b"\xa4\xb9\xcf\xae}\xbf\x01L\x10\xb4W~g\x96\x83\xe2N\xb5'v;\x91\xcb\x80&\xf2F\xa2\x1d\x93\xffD"
    
def test_node():
    n1 = core.Node(1, {'product':'corn','ammount':1500})
    
    assert n1.to_json() == '{"timestamp": null, "unique_id": 1, "payload": {"product": "corn", "ammount": 1500}, "attachments": [], "extra_hash": null, "hash_chain": null, "signature": null}'
    
    with freeze_time(datetime(2018,6,1,1,23, tzinfo=timezone.utc)):
        assert datetime.now(timezone.utc) == datetime(2018,6,1,1,23, tzinfo=timezone.utc)
        n1_hash_chain = n1.hash_chain()
    
    assert n1_hash_chain.make_playload() == b"\x01\x12A\x1d\xf5DB*}\\\xc3%\x05)&\x8d\x0c!V[\xc3T\x8fz\xfe\xa3\x9c\xa6\x1b'($\x01"
    
    assert n1.to_json() == '{"timestamp": "2018-06-01T01:23:00.000000+00:00", "unique_id": 1, "payload": {"product": "corn", "ammount": 1500}, "attachments": [], "extra_hash": null, "hash_chain": "ARJBHfVEQip9XMMlBSkmjQwhVlvDVI96/qOcphsnKCQB", "signature": null}'
    
    n1.sign_data(method='sha256')
    
    assert n1.to_json() == '{"timestamp": "2018-06-01T01:23:00.000000+00:00", "unique_id": 1, "payload": {"product": "corn", "ammount": 1500}, "attachments": [], "extra_hash": null, "hash_chain": "ARJBHfVEQip9XMMlBSkmjQwhVlvDVI96/qOcphsnKCQB", "signature": "ATIwMTgtMDYtMDFUMDE6MjM6MDAuMDAwMDAwKzAwOjAwMTE="}'
    
    # email.mime.multipart.MIMEMultipart mocking
    core.MIMEMultipart = partial(core.MIMEMultipart, boundary='===============3353248956693792728==')
    # print(n1.to_flat_file().decode('utf-8'))
    assert n1.to_flat_file().decode('utf-8') == '''Content-Type: multipart/mixed; boundary="===============3353248956693792728=="
MIME-Version: 1.0

--===============3353248956693792728==
timestamp: 2018-06-01T01:23:00.000000+00:00
hash_chain: 0112411DF544422A7D5CC3250529268D0C21565BC3548F7AFEA39CA61B27282401


--===============3353248956693792728==
Content-Type: application/octet-stream; description="payload"
MIME-Version: 1.0
Content-Transfer-Encoding: 8bit

{"x":"ç"}
--===============3353248956693792728==--
'''
    
    
