"""Personal income-tax calculator (teaching example, modelled on FY 2025-26).

The slabs are for teaching only and are not tax advice.

Set PAN_KEY_HEX to a 64-character hex string (32 bytes) before encrypting
PAN numbers, for example:
    export PAN_KEY_HEX=$(python -c "import os;print(os.urandom(32).hex())")
"""
import os
import re
# wsgiref's CGIHandler ignores HTTP_PROXY, so the httpoxy warning is safe here
from wsgiref.handlers import CGIHandler  # nosec B412

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from defusedxml import minidom

# Slabs as configured for this program (modelled on FY 2025-26)
STANDARD_DEDUCTION_NEW = 75000
STANDARD_DEDUCTION_OLD = 50000
REBATE_LIMIT_NEW = 1200000
LIMIT_80C = 150000
CESS = 0.04

NEW_SLABS = [
    (400000, 0.0),
    (800000, 0.05),
    (1200000, 0.10),
    (1600000, 0.15),
    (2000000, 0.20),
    (2400000, 0.25),
    (float("inf"), 0.30),
]
OLD_SLABS = [
    (250000, 0.0),
    (500000, 0.05),
    (1000000, 0.20),
    (float("inf"), 0.30),
]


def slab_tax(taxable, slabs, start=0):
    """Return tax computed slab by slab, beginning at `start`."""
    total = 0
    lower = start
    for upper, rate in slabs:
        if taxable > lower:
            total += (min(taxable, upper) - lower) * rate
        lower = max(lower, upper)
    return total


def new_regime_tax(salary):
    """Return new-regime tax (including 87A rebate and cess)."""
    taxable = max(salary - STANDARD_DEDUCTION_NEW, 0)
    if taxable <= REBATE_LIMIT_NEW:
        return 0
    return int(slab_tax(taxable, NEW_SLABS) * (1 + CESS))


def basic_exemption(age):
    """Return the basic exemption limit for the given age."""
    if age >= 80:
        return 500000
    if age >= 60:
        return 300000
    return 250000


def old_regime_tax(salary, age, deductions):
    """Return old-regime tax (including cess) after deductions."""
    capped = dict(deductions)
    if "80C" in capped:
        capped["80C"] = min(capped["80C"], LIMIT_80C)
    taxable = salary - STANDARD_DEDUCTION_OLD - sum(capped.values())
    taxable = max(taxable, 0)
    total_tax = slab_tax(taxable, OLD_SLABS, start=basic_exemption(age))
    return int(total_tax * (1 + CESS))


def better_regime(salary, age, deductions):
    """Return 'new' or 'old', whichever gives the lower tax."""
    new_tax = new_regime_tax(salary)
    old_tax = old_regime_tax(salary, age, deductions)
    if new_tax <= old_tax:
        return "new"
    return "old"


def is_valid_pan(pan):
    """Return True if `pan` is exactly five letters, four digits, a letter."""
    return isinstance(pan, str) and bool(
        re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan)
    )


def _pan_key():
    """Read the 32-byte AES key from the environment."""
    key_hex = os.environ.get("PAN_KEY_HEX")
    if key_hex is None:
        raise RuntimeError("PAN_KEY_HEX is not set (64 hex characters).")
    return bytes.fromhex(key_hex)


def encrypt_pan(pan):
    """Encrypt a PAN with AES-GCM and a random nonce; return hex text."""
    nonce = os.urandom(12)
    cipher_text = AESGCM(_pan_key()).encrypt(nonce, pan.encode(), None)
    return (nonce + cipher_text).hex()


def signing_key():
    """Generate a 2048-bit RSA signing key."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def parse_form16(xml_text):
    """Return (salary, tds) read from a Form-16 XML string."""
    doc = minidom.parseString(xml_text)
    salary_text = doc.getElementsByTagName("salary")[0].firstChild.data
    tds_text = doc.getElementsByTagName("tds")[0].firstChild.data
    return int(salary_text), int(tds_text)


def run_as_cgi(app):
    """Run a WSGI application as a CGI script."""
    CGIHandler().run(app)  # nosec B412


def main():
    """Print a demonstration of the calculator."""
    print("New regime, salary 12,75,000:", new_regime_tax(1275000))
    print("New regime, salary 18,00,000:", new_regime_tax(1800000))
    deductions = {"80C": 200000, "80D": 30000}
    print("Old regime, salary 18,00,000:",
          old_regime_tax(1800000, 35, deductions))
    print(f"Better regime: {better_regime(1800000, 35, deductions)}")
    print(f"Basic exemption at age 80: {basic_exemption(80)}")
    print("PAN 'ABCDE1234FXYZ' valid?", is_valid_pan("ABCDE1234FXYZ"))
    try:
        same = encrypt_pan("ABCDE1234F") == encrypt_pan("ABCDE1234F")
        print("Same PAN encrypts the same way twice?", same)
    except RuntimeError as err:
        print("Skipping PAN encryption demo:", err)
    form16 = "<form16><salary>1800000</salary><tds>150000</tds></form16>"
    print("Form 16:", parse_form16(form16))
    print(f"Signing key size: {signing_key().key_size}")


if __name__ == "__main__":
    main()
