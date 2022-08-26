import json


def keyapi():
    # path = input("Paste file location. If not exist,
    # paste location where would you like to be your API Keys stored: ")
    print("api_keys.py: Create saving path to API in config file.")
    path = "C:/Users/Lenovo/private"
    while True:
        try:
            with open(f"{path}/api_keys.json", 'r') as dataread:
                output_data = json.load(dataread)

        except FileNotFoundError:
            print("API config file not found, creating new API config file...")

            api_key = input("Input your API Key: ")
            secret_key = input("Input your API Secret Key: ")

            input_data = {"api_key": api_key,
                          "secret_key": secret_key}

            with open(f"{path}/api_keys.json", 'w') as datasave:
                json.dump(input_data, datasave, indent=4)

        else:
            api_key = output_data["api_key"]
            secret_key = output_data["secret_key"]
            break

    return api_key, secret_key


"""
# ----- test -------:
a,b = keyapi()

print(a)
print(b)
"""