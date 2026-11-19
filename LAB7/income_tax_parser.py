def clean_pan(pan):
    if not isinstance(pan, str):
        return ""
    return pan.strip().replace(' ', '').upper()

def parse_amount(text):
    if not isinstance(text, str):
        return None
    text = text.replace('Rs', '').replace(',', '').strip()
    try:
        return int(text)
    except ValueError:
        return None

def parse_tax_slab(line):
    if not isinstance(line, str):
        return None
    try:
        limits, rate = line.split(':')
        low, high = limits.split('-')
        return int(low), int(high), int(rate)
    except ValueError:
        return None

def main():
    print("==== Running clean_pan ====")
    value = input("Enter a PAN (e.g. abcde 1234f): ")
    print("Cleaned PAN:", clean_pan(value))

    print("\n==== Running parse_amount ====")
    value = input("Enter an amount (e.g. Rs 12,50,000): ")
    print("Amount in rupees:", parse_amount(value))

    print("\n==== Running parse_tax_slab ====")
    value = input("Enter a tax slab as LOW-HIGH:RATE (e.g. 250000-500000:5): ")
    print("Tax slab (low, high, rate):", parse_tax_slab(value))

if __name__ == "__main__":
    main()