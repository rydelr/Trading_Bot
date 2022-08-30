import json
import os


def save_parameter(pair: str, kwarg: str, value):

    file_name = f"config/{pair.upper()}/parameters/parameters_config.json"

    try:
        with open(file_name, "r+") as dataread:
            output_data = json.load(dataread)

    except FileNotFoundError:
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, "w") as new_file:
            input_data = {str(kwarg): value, }
            json.dump(input_data, new_file, indent=4, sort_keys=True)

    else:
        output_data[str(kwarg)] = value

        with open(file_name, "w") as overwrite:
            json.dump(output_data, overwrite, indent=4, sort_keys=True)


# ----- tests -----
"""
save_parameter("xmrusdt", "abc", 10.4)
save_parameter("xmrusdt", "abc", 10.4)
save_parameter("xmrusdt", 10, 20)
"""


def load_parameter(pair: str, kwarg: str):
    file_name = f"config/{pair.upper()}/parameters/parameters_config.json"
    while True:
        try:
            with open(file_name, "r+") as dataread:
                output_data = json.load(dataread)
                output = output_data[str(kwarg)]
                return output

        except FileNotFoundError:
            save_parameter(pair, kwarg, 0)

