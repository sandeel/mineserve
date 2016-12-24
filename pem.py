from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

certificate_text = open('/home/ubuntu/jwtkey.pem', 'rb').read()
certificate = load_pem_x509_certificate(certificate_text, default_backend())
publicKey = certificate.public_key()
