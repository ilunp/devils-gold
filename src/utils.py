import uuid
import hashlib
import re


def create_uuid_from_string(val: str) -> str:
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))


def clean_file_name(name: str) -> str:
    # Removes invalid chars from a filename str
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", name)
