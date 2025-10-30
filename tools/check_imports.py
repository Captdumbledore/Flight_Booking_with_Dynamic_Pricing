import importlib, traceback, os, sys

# Ensure project root (parent of tools/) is on sys.path so we can import project packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def try_import(name):
    print('--- Importing', name, '---')
    try:
        mod = importlib.import_module(name)
        print('OK:', name, '->', mod)
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    try_import('main')
    try_import('app.main')
