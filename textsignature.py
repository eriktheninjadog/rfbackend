import hashlib

def generate_signature(txt):
    encoded_str = txt.encode()
    hash_obj_sha256 = hashlib.sha256(encoded_str)
    text_signature = hash_obj_sha256.hexdigest()
    return text_signature
    