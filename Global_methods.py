# import base64
#
#
# def string_to_urlsafe_base64_bytes(input_string):
#     # Convert the string to bytes using UTF-8 encoding
#     bytes_data = input_string.encode('utf-8')
#
#     # Encode the bytes using base64 encoding
#     encoded_bytes = base64.urlsafe_b64encode(bytes_data)
#
#     # Remove any padding from the encoded bytes
#     encoded_bytes = encoded_bytes.rstrip(b'=')
#
#     # Pad the encoded bytes to ensure they are of the correct length (32 bytes)
#     padded_bytes = encoded_bytes.ljust(32, b'=')
#
#     return padded_bytes
#
#
