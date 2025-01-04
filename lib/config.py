"""
Import Statements Necessary for Program Configuration Reading
"""
import json
import os
import re
# -------------------------------------------#
"""
Class: Config
Purpose: To read in the program input and output file configurations
"""
class Config():

    def __init__(self):
        """
        Initializing the attributes of config.json location.
        """
        # Configuration File Location
        self.config_dir = "__CONFIG DIRECTORY__"
        self.config_nm = "config.json"
        self.config_path = os.path.join(self.config_dir, self.config_nm)

        # Attribute Placeholders
        self.input_cfg = dict()
        self.output_cfg = dict()
        self.summary_cfg = dict()

# -------------------------------------------#

    def get_config(self):
        """
        Retrieves the input, output, and logging configurations from the config.json
        """
        # Open and read the JSON file
        with open(self.config_path, 'r') as file:
            data = json.load(file)
            # Input Config
            self.input_cfg = {
                "location": data["locations"]["input"], 
                "prefix": data["naming_convention"]["input"]["pre"], 
                "extension": data["naming_convention"]["input"]["ext"]
            }
            # Output Config
            self.output_cfg = {
                "location": data["locations"]["output"], 
                "prefix": data["naming_convention"]["output"]["pre"], 
                "extension": data["naming_convention"]["output"]["ext"]
            }
            # Logging Config:
            self.summary_cfg = {
                "location": data["locations"]["summary"], 
                "prefix": data["naming_convention"]["summary"]["pre"], 
                "extension": data["naming_convention"]["summary"]["ext"]
            }
            # Function Arguments:
            self.func_args = {
                "start_cap": data["function_args"]["start_capital"],
                "start_dt": data["function_args"]["start_date"],
                "req_ret": data["function_args"]["required_return"]
            }

        # Assert configurations are correct
        assert os.path.exists(self.input_cfg["location"]), "Input file location does not exist"
        assert os.path.exists(self.output_cfg["location"]), "Output file location does not exist"
        assert os.path.exists(self.summary_cfg["location"]), "Summary file location does not exist"
        assert (self.output_cfg["extension"][0] == ".") & (self.input_cfg["extension"][0] == ".") & (self.summary_cfg["extension"][0] == "."), "Input and/or ouput and/or summary configurated extensions do not start with '.'"
        assert self.func_args["start_cap"] > 0, "Starting capital is less than or equal to zero"
        assert re.fullmatch(r'[0-9]{2}/[0-9]{2}/[0-9]{4}', self.func_args["start_dt"]), "Start date does not follow the format mm/dd/yyyy"
        assert self.func_args["req_ret"] > 0, "Required return is less than or equal to zero"
        
# -------------------------------------------#