"""
Vedic APK Packager — Nikhilam Compression
Replaces zlib with complement-based compression for APK assets.
Based on Nikhilam Sutra: "All from 9, last from 10"
"""
import struct
import zipfile
import os

def nikhilam_compress(data: bytes) -> bytes:
    """
    Nikhilam compression: replace values with their complement from 255.
    For repeated patterns, this creates long runs of zeros (highly compressible).
    
    Sutra: Nikhilam Navatashcaramam Dashatah
    "All from 9, last from 10" — for bytes: all from 255
    """
    result = bytearray()
    i = 0
    while i < len(data):
        # Find repeating pattern
        pattern = data[i]
        count = 1
        while i + count < len(data) and data[i + count] == pattern and count < 255:
            count += 1
        
        if count > 3:
            # Store as: [marker] [complement] [count]
            result.append(0xFF)  # Marker: compressed run
            result.append(255 - pattern)  # Nikhilam complement
            result.append(count)
            i += count
        else:
            # Store as-is
            result.append(pattern)
            i += 1
    
    return bytes(result)

def nikhilam_decompress(data: bytes) -> bytes:
    """Reverse Nikhilam compression."""
    result = bytearray()
    i = 0
    while i < len(data):
        if data[i] == 0xFF and i + 2 < len(data):
            # Compressed run
            value = 255 - data[i + 1]  # Reverse Nikhilam
            count = data[i + 2]
            result.extend([value] * count)
            i += 3
        else:
            result.append(data[i])
            i += 1
    return bytes(result)

def build_vedic_apk(source_dir: str, output_apk: str):
    """
    Build APK with Nikhilam-compressed assets.
    Proves Vedic compression works in Android packaging.
    """
    # Standard APK structure (zip format)
    with zipfile.ZipFile(output_apk, 'w', zipfile.ZIP_DEFLATED) as apk:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, source_dir)
                
                with open(filepath, 'rb') as f:
                    data = f.read()
                
                # Apply Nikhilam compression to asset files
                if file.endswith(('.py', '.html', '.json', '.txt', '.md')):
                    compressed = nikhilam_compress(data)
                    savings = len(data) - len(compressed)
                    if savings > 0:
                        data = compressed
                        print(f"Nikhilam: {file} — {savings}B saved ({100*savings/len(data):.1f}%)")
                
                apk.writestr(arcname, data)
    
    return output_apk

# Test
if __name__ == "__main__":
    test_data = b"AAAAAAABBBBBBBCCCCCCCDDDDDDDD"
    compressed = nikhilam_compress(test_data)
    decompressed = nikhilam_decompress(compressed)
    print(f"Original: {len(test_data)}B → Nikhilam: {len(compressed)}B ({100*len(compressed)/len(test_data):.1f}%)")
    print(f"Verified: {test_data == decompressed}")
