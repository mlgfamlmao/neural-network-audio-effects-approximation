import glob
def get_files():
    
    files = glob.glob("TinySOL/**/*.wav", recursive=True)
    return files