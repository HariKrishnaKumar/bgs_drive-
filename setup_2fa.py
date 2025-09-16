import pyotp
import qrcode

# Generate a new secret key
# In a real app, you would save this secret securely for the user.
secret_key = pyotp.random_base32()

# The provisioning URI is a standard format that authenticator apps understand.
# Replace 'admin@bgsdrive.com' with your actual username/email.
# Replace 'BGS Drive' with your application's name.
provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
    name='myadmin@bgs.com',
    issuer_name='BGS Drive'
)

print("--- 2FA Setup ---")
print(f"Your 2FA Secret Key is: {secret_key}")
print("A QR code has been saved as 'qrcode.png'. Scan it with your Google Authenticator app.")
print("IMPORTANT: Copy the secret key above and paste it into the SECRET_KEY variable in main.py")

# Generate the QR code image
img = qrcode.make(provisioning_uri)
img.save("qrcode.png")