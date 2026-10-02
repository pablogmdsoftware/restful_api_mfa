from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password):
    return password_hash.hash(password)