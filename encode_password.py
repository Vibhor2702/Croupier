"""Quick script to URL encode your MongoDB password"""
from urllib.parse import quote_plus

print("MongoDB Password URL Encoder")
print("-" * 40)
password = input("Enter your MongoDB password: ")
encoded = quote_plus(password)
print(f"\nOriginal: {password}")
print(f"Encoded:  {encoded}")
print(f"\nIf they're different, use the ENCODED version in your .env file")
print(f"\nYour connection string should look like:")
print(f"mongodb+srv://username:{encoded}@cluster.mongodb.net/...")
