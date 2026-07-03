import hashlib


def hash_file_content(file: str) -> str:
    with open(file, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def hash_text(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


hash_content = hash_text
