from pathlib import Path
import subprocess,tarfile,hashlib,json,sqlite3,tempfile,os
import argparse
parser=argparse.ArgumentParser(description='Verify an encrypted Orgo GTM backup without extracting its files.')
parser.add_argument('--backup-dir',type=Path,required=True)
parser.add_argument('--archive-name',default='orgo-gtm-application-backup.tar.gz.cms')
args=parser.parse_args()
r=args.backup_dir
archive_name=args.archive_name
from gtm_cms_stream import CMSReader
source=(r/archive_name).open('rb')
reader=CMSReader(source,r/'restore-private-key.pem')
actual={};checks={};meta=None
with tarfile.open(fileobj=reader,mode='r|gz') as archive:
 for member in archive:
  if member.name=='backup-metadata/file-manifest.json':
   meta=json.load(archive.extractfile(member));continue
  if member.issym():actual[member.name]={'type':'symlink','target':member.linkname};continue
  if not member.isfile():continue
  h=hashlib.sha256();f=archive.extractfile(member);temp=None;out=None
  if member.name=='root/.hermes/state.db' or (member.name.startswith('root/.hermes/profiles/') and member.name.endswith('/state.db')):
   fd,temp=tempfile.mkstemp(prefix='gtm-restore-check-',suffix='.sqlite');os.chmod(temp,0o600);out=os.fdopen(fd,'wb')
  while True:
   chunk=f.read(4*1024*1024)
   if not chunk:break
   h.update(chunk)
   if out:out.write(chunk)
  actual[member.name]={'sha256':h.hexdigest(),'bytes':member.size}
  if out:
   out.close()
   conn=sqlite3.connect('file:'+temp+'?mode=ro',uri=True);check=conn.execute('PRAGMA quick_check').fetchall();conn.close();Path(temp).unlink()
   assert check==[('ok',)],(member.name,check);checks[member.name]='ok'
reader.read();source.close()
assert meta is not None
for entry in meta['files']:
 a=actual.get(entry['path']);assert a is not None,entry['path']
 if entry.get('type')=='symlink':assert a['target']==entry['target']
 else:assert a['sha256']==entry['sha256'] and a['bytes']==entry['bytes'],entry['path']
assert len(actual)==len(meta['files'])
(r/(archive_name+'.file-manifest.private.json')).write_text(json.dumps(meta,indent=2)+'\n');os.chmod(r/(archive_name+'.file-manifest.private.json'),0o600)
summary={'computer_id':meta['computer_id'],'computer_name':meta['computer_name'],'created_utc':meta['created_utc'],'files_verified':len(actual),'archive_uncompressed_bytes':sum(x.get('bytes',0) for x in actual.values()),'capture_errors':meta['errors'],'sqlite_quick_checks':checks,'encrypted_bytes':(r/archive_name).stat().st_size,'encrypted_sha256':hashlib.file_digest((r/archive_name).open('rb'),'sha256').hexdigest(),'roots':meta['roots'],'excluded_prefixes':meta['excluded_prefixes'],'excluded_directory_names':meta['excluded_directory_names'],'scope':meta['scope']}
(r/(archive_name+'.VERIFICATION.json')).write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['files_verified','capture_errors','encrypted_bytes']},indent=2))
