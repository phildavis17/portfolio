SPECIAL_FACTORS = {
    3: "fizz",
    5: "buzz",
}

def fizzbuzz(n: int) -> str:
    output = ""
    for factor, message in SPECIAL_FACTORS.items():
        if n % factor == 0:
            output += message
    return output or str(n)

if __name__ == "__main__":
    for i in range(1, 101):
        print(fizzbuzz(i))