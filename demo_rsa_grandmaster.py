#!/usr/bin/env python3
"""
🔐 AURORA RSA GRANDMASTER DEMONSTRATION
Complete showcase of RSA cryptography mastery
"""

from aurora_rsa_grandmaster import AuroraRSAGrandmaster, PaddingScheme

print("\n" + "="*70)
print("🔐 AURORA RSA GRANDMASTER - COMPREHENSIVE DEMONSTRATION")
print("="*70 + "\n")

rsa = AuroraRSAGrandmaster()

# ============================================================================
# DEMONSTRATION 1: SECURE KEY GENERATION
# ============================================================================
print("\n📋 DEMONSTRATION 1: Secure Key Generation")
print("-" * 70)

public_1024, private_1024 = rsa.generate_keypair(bits=1024)
print(f"✅ Generated 1024-bit keypair")
print(f"   Modulus (n): {str(public_1024.n)[:60]}...")
print(f"   Public exponent (e): {public_1024.e}")
print(f"   Key strength: {public_1024.n.bit_length()} bits")

# ============================================================================
# DEMONSTRATION 2: ENCRYPTION & DECRYPTION
# ============================================================================
print("\n\n📋 DEMONSTRATION 2: Encryption & Decryption")
print("-" * 70)

messages = [
    b"Hello, Aurora!",
    b"RSA encryption is powerful",
    b"Quantum computers will break this... eventually",
]

for i, msg in enumerate(messages, 1):
    print(f"\nMessage {i}: {msg.decode()}")
    ciphertext = rsa.encrypt(msg, public_1024, PaddingScheme.NONE)
    print(f"  Encrypted: {str(ciphertext)[:60]}...")

    result = rsa.decrypt(ciphertext, private_1024, PaddingScheme.NONE)
    print(f"  Decrypted: {result.plaintext.decode()}")
    print(f"  Success: {result.success} | Method: {result.method}")

# ============================================================================
# DEMONSTRATION 3: CRYPTANALYSIS - FACTORIZATION
# ============================================================================
print("\n\n📋 DEMONSTRATION 3: Cryptanalysis - Factorization Attacks")
print("-" * 70)

print("\nTrying to factor different key sizes...")

# Small key (insecure)
print("\n• 128-bit key (INSECURE):")
weak_pub, weak_priv = rsa.generate_keypair(bits=128)
factors = rsa.factor_modulus(weak_pub.n)
if factors:
    p, q = factors
    print(f"  ⚠️  BROKEN! Factors found:")
    print(f"     p = {p}")
    print(f"     q = {q}")
    print(f"     Verification: p × q = n? {p * q == weak_pub.n}")

# Medium key
print("\n• 512-bit key:")
medium_pub, _ = rsa.generate_keypair(bits=512)
factors = rsa.factor_modulus(medium_pub.n)
if factors:
    print(f"  ⚠️  Factors found (weak key)")
else:
    print(f"  ✅ Factorization failed (key is reasonably strong)")

# ============================================================================
# DEMONSTRATION 4: WIENER'S ATTACK (Small Private Exponent)
# ============================================================================
print("\n\n📋 DEMONSTRATION 4: Wiener's Attack")
print("-" * 70)

print("Attempting Wiener's attack on weak key...")
# This would require a specially crafted weak key
# For demonstration, we'll show the attack attempt
result = rsa.wieners_attack(public_1024)
if result:
    print(f"  ⚠️  BROKEN! Private exponent found: d={result}")
else:
    print(f"  ✅ Attack failed - key is secure against Wiener's attack")

# ============================================================================
# DEMONSTRATION 5: COMMON MODULUS ATTACK
# ============================================================================
print("\n\n📋 DEMONSTRATION 5: Common Modulus Attack")
print("-" * 70)

# Create scenario: same message encrypted with different exponents
plaintext_int = 12345
e1, e2 = 65537, 3
n = public_1024.n

c1 = pow(plaintext_int, e1, n)
c2 = pow(plaintext_int, e2, n)

print(f"Original message: {plaintext_int}")
print(f"Encrypted with e1={e1}: {str(c1)[:60]}...")
print(f"Encrypted with e2={e2}: {str(c2)[:60]}...")

recovered = rsa.common_modulus_attack(c1, c2, e1, e2, n)
if recovered:
    print(f"⚠️  ATTACK SUCCESSFUL! Recovered message: {recovered}")
else:
    print(f"Attack failed")

# ============================================================================
# DEMONSTRATION 6: SMALL EXPONENT ATTACK
# ============================================================================
print("\n\n📋 DEMONSTRATION 6: Small Exponent Attack")
print("-" * 70)

# Weak scenario: small exponent without proper padding
small_msg = 99
e_small = 3
c_weak = pow(small_msg, e_small)

print(f"Original message: {small_msg}")
print(f"Encrypted with e={e_small} (NO PADDING): {c_weak}")

recovered = rsa.small_e_attack(c_weak, e_small, n)
if recovered == small_msg:
    print(f"⚠️  ATTACK SUCCESSFUL! Recovered: {recovered}")
    print(f"  Lesson: ALWAYS use proper padding!")
else:
    print(f"Attack failed or message mismatch")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n\n" + "="*70)
print("📊 AURORA RSA GRANDMASTER - CAPABILITY SUMMARY")
print("="*70)

summary = rsa.get_capabilities_summary()
print(f"\n🔐 Tier: {summary['tier']}")
print(f"📛 Name: {summary['name']}")
print(f"🔢 Version: {summary['version']}")
print(f"✅ Status: {summary['status'].upper()}")

print(f"\n🛡️  Core Capabilities ({len(summary['capabilities'])}):")
for cap in summary['capabilities']:
    print(f"  • {cap}")

print(f"\n⚔️  Attack Techniques ({len(summary['attack_types'])}):")
for attack in summary['attack_types']:
    print(f"  • {attack}")

print(f"\n🔒 Padding Schemes ({len(summary['padding_schemes'])}):")
for scheme in summary['padding_schemes']:
    print(f"  • {scheme}")

print("\n" + "="*70)
print("🎯 KEY TAKEAWAYS:")
print("="*70)
print("1. ✅ RSA is secure with proper key sizes (2048+ bits)")
print("2. ✅ Always use proper padding (OAEP preferred)")
print("3. ⚠️  Small exponents are dangerous without padding")
print("4. ⚠️  Never reuse modulus with different exponents")
print("5. ⚠️  Keys under 1024 bits are vulnerable to factorization")
print("6. ✅ Aurora can both secure AND break RSA implementations")
print("="*70 + "\n")
