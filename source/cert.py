#!/usr/bin/env python3
import urllib.request

url = "https://pki.google.com/roots.pem"
filename = "roots.pem"

with urllib.request.urlopen(url) as response, open(filename, 'wb') as file:
    content = response.read() # a `bytes` object
    file.write(content)
