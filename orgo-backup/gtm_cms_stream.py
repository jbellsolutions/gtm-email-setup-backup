"""Streaming reader for this backup's single-recipient OpenSSL CMS AES-256-CBC format."""
import io,time
from cryptography.hazmat.primitives import serialization,padding
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
class CMSReader:
 def __init__(self,source,key_path,wait=None):
  self.source=source;self.wait=wait;self.buf=bytearray();self.finished=False
  self.expect_header(0x30,None)
  assert self.node(6)==bytes.fromhex('2a864886f70d010703')
  self.expect_header(0xa0,None);self.expect_header(0x30,None);self.node(2)
  recipient=io.BytesIO(self.node(0x31))
  h=self.header(recipient);assert h[0]==0x30
  self.node(2,recipient);self.node(0x30,recipient)
  alg=self.node(0x30,recipient);assert bytes.fromhex('2a864886f70d010101') in alg
  wrapped=self.node(4,recipient)
  self.expect_header(0x30,None);assert self.node(6)==bytes.fromhex('2a864886f70d010701')
  alg=io.BytesIO(self.node(0x30));assert self.node(6,alg)==bytes.fromhex('60864801650304012a')
  iv=self.node(4,alg);assert len(iv)==16
  key=serialization.load_pem_private_key(key_path.read_bytes(),password=None)
  secret=key.decrypt(wrapped,rsa_padding.PKCS1v15());assert len(secret)==32
  self.decrypt=Cipher(algorithms.AES(secret),modes.CBC(iv)).decryptor()
  self.unpad=padding.PKCS7(128).unpadder();self.expect_header(0xa0,None)
 def exact(self,n,source=None):
  source=source or self.source;out=bytearray()
  while len(out)<n:
   b=source.read(n-len(out))
   if b:out.extend(b)
   elif source is self.source and self.wait and self.wait():time.sleep(.2)
   else:raise EOFError('Truncated CMS backup')
  return bytes(out)
 def header(self,source=None):
  tag,n=self.exact(2,source)
  if n==0x80:return tag,None
  if n&0x80:n=int.from_bytes(self.exact(n&0x7f,source),'big')
  return tag,n
 def expect_header(self,tag,n):
  assert self.header()==(tag,n),'Unsupported CMS structure'
 def node(self,tag,source=None):
  t,n=self.header(source);assert t==tag and n is not None
  return self.exact(n,source)
 def next(self):
  tag,n=self.header()
  if (tag,n)==(0,0):
   tail=self.decrypt.finalize();self.buf.extend(self.unpad.update(tail)+self.unpad.finalize())
   for _ in range(4):self.expect_header(0,0)
   self.finished=True;return
  assert tag==4 and n is not None and 0<n<=1024*1024,'Unsupported CMS content chunk'
  self.buf.extend(self.unpad.update(self.decrypt.update(self.exact(n))))
 def read(self,n=-1):
  if n<0:
   while not self.finished:self.next()
   out=bytes(self.buf);self.buf.clear();return out
  while len(self.buf)<n and not self.finished:self.next()
  out=bytes(self.buf[:n]);del self.buf[:n];return out
if __name__=='__main__':
 import argparse,sys
 from pathlib import Path
 p=argparse.ArgumentParser(description='Stream-decrypt the GTM Orgo AES-256-CBC CMS backup.')
 p.add_argument('archive',type=Path);p.add_argument('--key',type=Path,required=True);a=p.parse_args()
 with a.archive.open('rb') as f:
  reader=CMSReader(f,a.key)
  while data:=reader.read(1024*1024):sys.stdout.buffer.write(data)
