import struct

buf = bytearray()
symbols = {}          # name -> offset
patches = []          # (target_name, placeholder_offset)

def mark(name):
    """Remember the current offset as 'name'."""
    symbols[name] = len(buf)

def w_ptr(target):
    """Write a 4-byte placeholder and record where to patch later."""
    patches.append((target, len(buf)))
    buf.extend(b'\xFF\xFF\xFF\xFF')   # placeholder

def w_raw(data):
    buf.extend(data)

def w_str(text):
    while len(buf) % 4 != 0:          # align to 4 bytes
        buf.append(0)
    raw = text.encode('utf-8') + b'\x00'
    buf.extend(raw)
    while len(buf) % 4 != 0:          # align to 4 bytes
        buf.append(0)

buf.extend(bytes.fromhex("FF"))
w_str("The End\nTime")
w_str("Now...")
w_str("\n\nkappa")

buf.extend(b'\xAA' * 255)

# ---------- Build the file ----------
# Section "strings": write some data
mark("strings")
w_raw(b'Hello World\x00')

# Section "header": contains a pointer to "strings"
mark("header")
w_ptr("strings")          # pointer placeholder
w_raw(b'\x01\x02\x03')    # some extra bytes after pointer

# ---------- Patch all pointers ----------
for target, pos in patches:
    struct.pack_into('<I', buf, pos, symbols[target])

# ---------- Save ----------
with open('output.bin', 'wb') as f:
    f.write(buf)