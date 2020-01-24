compress_map = {
    "0000": "0",
    "0001": "1",
    "0010": "2",
    "0011": "3",
    "0100": "4",
    "0101": "5",
    "0110": "6",
    "0111": "7",
    "1000": "8",
    "1001": "9",
    "1010": "a",
    "1011": "b",
    "1100": "c",
    "1101": "d",
    "1110": "e",
    "1111": "f",
}
decompress_map = {
    "0": "0000",
    "1": "0001",
    "2": "0010",
    "3": "0011",
    "4": "0100",
    "5": "0101",
    "6": "0110",
    "7": "0111",
    "8": "1000",
    "9": "1001",
    "a": "1010",
    "b": "1011",
    "c": "1100",
    "d": "1101",
    "e": "1110",
    "f": "1111",
}


def compress(string: str) -> str:
    if len(string) % 4:
        string += "0" * (4 - len(string) % 4)

    compressed = ""

    i = 0
    while i < len(string):
        compressed += compress_map[string[i : i + 4]]

        i += 4

    return compressed


def decompress(string: str, length: int = 361) -> str:
    decompressed = ""

    for c in string:
        decompressed += decompress_map[c]

    return decompressed[:length]
