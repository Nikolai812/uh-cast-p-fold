import configparser
import os
import logging


def str_to_bool(value):
    return value.lower() in ('true', '1', 'yes', 'y', 't')

def load_config():
    config = configparser.ConfigParser()
    script_dir = os.path.dirname(os.path.abspath(__file__))  # folder where main.py is
    config_path = os.path.join(script_dir, "config.ini")
    config.read(config_path, encoding="utf-8")

    # Updating all relative paths from config to get the absolute values starting from the location of tha main.py file
    config['DEFAULT']['script_dir'] = script_dir
    data_lake_dir = os.path.join(script_dir, config['DEFAULT']['data_lake_dir'])
    print("data_lake_dir: ", config['DEFAULT']['data_lake_dir'])
    if not os.path.exists(data_lake_dir):
        raise FileNotFoundError(f"Data lake '{data_lake_dir}' does not exist, please reconfigure the pipeline")
    else:
        config['DEFAULT']['data_lake_dir'] = data_lake_dir
        print(f"Using Data Lake: {data_lake_dir}")

    config['DEFAULT']['input_dir'] = os.path.join(data_lake_dir, config['DEFAULT']['input_dir'])
    config['DEFAULT']['output_dir'] = os.path.join(data_lake_dir, config['DEFAULT']['output_dir'])

    config['DEFAULT']['pacupp_python_feedup'] = os.path.join(script_dir, config['DEFAULT']['pacupp_python_feedup'])
    # for web p2rank download:
    config['DEFAULT']['prankweb_temp'] = os.path.join(script_dir, config['DEFAULT']['prankweb_temp'])
    # for local p2rank run config path for output is absolute and needs not to be updated
    # End of relative path update

    logging.info(f"Configuration loaded from {config_path}, sections: {config.sections()} defaults: {config.defaults()}")
    version=config['DEFAULT']['version']
    logging.info(f"########## CAVITY PIPELINE VERSION: {version}")
    return config['DEFAULT']
