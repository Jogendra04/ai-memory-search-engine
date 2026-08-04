import hashlib


def get_file_hash(file_bytes):
    """
    Returns SHA-256 hash of a file.
    """

    return hashlib.sha256(file_bytes).hexdigest()