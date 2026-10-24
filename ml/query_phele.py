import urllib.request
import struct
import zlib
from concurrent.futures import ThreadPoolExecutor

PHELE_S3_URL = 'https://prod-dcd-datasets-public-files-eu-west-1.s3.eu-west-1.amazonaws.com/ec6ca432-75f6-491c-aa9d-2a268fd80782'
CD_OFFSET = 2517832913
CD_SIZE = 275723

req = urllib.request.Request(PHELE_S3_URL, headers={'Range': f'bytes={CD_OFFSET}-{CD_OFFSET + CD_SIZE - 1}'})
cd_data = urllib.request.urlopen(req, timeout=15).read()

pos = 0
label_entries = {}
while pos < len(cd_data) - 4:
    if cd_data[pos:pos+4] != b'\x50\x4b\x01\x02':
        break
    vals = struct.unpack('<HHHHHHIIIHHHHHII', cd_data[pos+4:pos+46])
    name = cd_data[pos+46:pos+46+vals[9]].decode('utf-8', errors='ignore')
    entry = {'name': name, 'offset': vals[15], 'comp_size': vals[7], 'method': vals[3]}
    if name.endswith('.txt') and name != 'PHELE/classes.txt':
        label_entries[name] = entry
    pos += 46 + vals[9] + vals[10] + vals[11]

def check_label(item):
    name, le = item
    try:
        req = urllib.request.Request(PHELE_S3_URL, headers={'Range': f"bytes={le['offset']}-{le['offset'] + 30 + len(name) + 100}"})
        hdr = urllib.request.urlopen(req, timeout=10).read()
        l_name_len, l_extra_len = struct.unpack('<HH', hdr[26:30])
        d_start = le['offset'] + 30 + l_name_len + l_extra_len
        d_end = d_start + le['comp_size'] - 1
        req2 = urllib.request.Request(PHELE_S3_URL, headers={'Range': f"bytes={d_start}-{d_end}"})
        raw = urllib.request.urlopen(req2, timeout=10).read()
        txt = zlib.decompress(raw, -15) if le['method'] == 8 else raw
        txt_str = txt.decode('utf-8', errors='ignore')
        for line in txt_str.splitlines():
            if line.strip().startswith('13 '):
                return (name, line.strip())
    except Exception:
        pass
    return None

with ThreadPoolExecutor(max_workers=16) as ex:
    results = list(filter(None, ex.map(check_label, label_entries.items())))

print(f"Total PHELE files containing Wet Floor (class 13): {len(results)}")
for name, line in results:
    print(f"  {name} -> {line}")
