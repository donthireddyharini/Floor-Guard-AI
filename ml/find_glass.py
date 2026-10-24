import urllib.request, struct

PHELE_S3_URL = 'https://prod-dcd-datasets-public-files-eu-west-1.s3.eu-west-1.amazonaws.com/ec6ca432-75f6-491c-aa9d-2a268fd80782'
CD_OFFSET = 2517832913
CD_SIZE = 275723

req = urllib.request.Request(PHELE_S3_URL, headers={'User-Agent': 'Mozilla/5.0', 'Range': f'bytes={CD_OFFSET}-{CD_OFFSET + CD_SIZE - 1}'})
with urllib.request.urlopen(req) as resp:
    cd_data = resp.read()

targets = ['train_524.jpg', 'train_524.txt', 'train_525.jpg', 'train_525.txt', 'train_533.jpg', 'train_533.txt', 'train_534.jpg', 'train_534.txt', 'train_552.jpg', 'train_552.txt']
for target in targets:
    idx = cd_data.find(target.encode())
    if idx != -1:
        h_idx = cd_data.rfind(b'\x50\x4b\x01\x02', 0, idx)
        vals = struct.unpack('<HHHHHHIIIHHHHHII', cd_data[h_idx+4:h_idx+46])
        fn = cd_data[h_idx+46:h_idx+46+vals[9]].decode('utf-8', errors='ignore')
        print(f'{target} -> name: "{fn}", offset: {vals[15]}, comp_size: {vals[7]}, method: {vals[3]}')
    else:
        print(f'{target} -> NOT FOUND')
