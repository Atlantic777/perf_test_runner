import hashlib

def hash_of_file(file_path):
        return hashlib.md5(open(file_path, "rb").read()).hexdigest()
