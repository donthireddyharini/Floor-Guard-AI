import urllib.request
import urllib.parse
import json

def search_wikimedia(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&format=json&srlimit=5"
    req = urllib.request.Request(url, headers={'User-Agent': 'FloorGuardAI/1.0 (test@floorguard.org)'})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode('utf-8'))
            results = data.get('query', {}).get('search', [])
            print(f'Wikimedia for "{query}":', [r['title'] for r in results])
    except Exception as e:
        print(f'Error for "{query}":', e)

if __name__ == '__main__':
    search_wikimedia('banana peel on floor')
    search_wikimedia('spilled food on floor')
    search_wikimedia('cables on floor')
    search_wikimedia('broken glass on floor')
    search_wikimedia('wet floor caution sign')
