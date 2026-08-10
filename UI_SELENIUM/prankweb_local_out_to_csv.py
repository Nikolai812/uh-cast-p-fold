import os
import csv

from configparser import SectionProxy
from datetime import datetime
import logging


import pandas as pd

from pathlib import Path
from file_namer import FileNamer, MethodType
from utils import str_to_bool, load_config


logger = logging.getLogger(__name__)



def process_p2rank_local_output(pdb_files, config):
    p2rank_local_output_dir = Path(config['prankweb_local_output'])

    for pdb_file in pdb_files:
        pdb_name = Path(pdb_file).stem
        predict_dir = p2rank_local_output_dir / f"predict_{pdb_name}"

        if not predict_dir.is_dir():
            logger.warning(
                "P2Rank output directory does not exist for %s: %s, processing skipped",
                pdb_file,
                predict_dir
            )
            continue

        # Further processing will be added here
        logger.info(f'PrankWeb local output processing for {pdb_file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
        output_dir = config['output_dir']
        process_prankweb_output(str(predict_dir), pdb_name, output_dir)


def process_prankweb_output(local_prankweb_output_dir, pdb_name, output_dir):
    """
    Processes the PRANKWeb output files in the specified directory.
    Args:
        local_prankweb_output_dir (str): Path to the directory containing the output files.
    Returns:
        tuple: (cav_residues, res_label_name) dictionaries, or (None, None) if files are missing.
    """
    # Initialize dictionaries
    cav_residues = {}
    res_label_name = {}

    # Define expected filenames
    predictions_file = f"{pdb_name}.pdb_predictions.csv" # "structure.pdb_predictions.csv"
    residues_file = f"{pdb_name}.pdb_residues.csv" #"structure.pdb_residues.csv"

    # Check if files exist
    if not os.path.exists(os.path.join(local_prankweb_output_dir, predictions_file)):
        logger.error(f"Error: '{predictions_file}' not found in '{local_prankweb_output_dir}'.")
        return None, None
    if not os.path.exists(os.path.join(local_prankweb_output_dir, residues_file)):
        logger.error(f"Error: '{residues_file}' not found in '{local_prankweb_output_dir}'.")
        return None, None

    # Read structure.pdb_predictions.csv into cav_residues
    with open(os.path.join(local_prankweb_output_dir, predictions_file), mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                stripped_row = {k.strip(): v.strip() for k, v in row.items()}
                cavity_number = int(stripped_row['rank'])
                residue_ids = stripped_row['residue_ids']
                cav_residues[cavity_number] = residue_ids
            except KeyError:
                logger.error(f"Warning: Missing 'rank' or 'residue_ids' column in '{predictions_file}'.")
            except ValueError:
                logger.error(f"Warning: 'rank' value '{row['rank']}' is not an integer.")

    # Read structure.pdb_residues.csv into res_label_name
    with open(os.path.join(local_prankweb_output_dir, residues_file), mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                stripped_row = {k.strip(): v.strip() for k, v in row.items()}
                residue_label = stripped_row['residue_label']
                residue_name = stripped_row['residue_name']
                res_label_name[residue_label] = residue_name
            except KeyError:
                logger.warning(f"Missing 'residue_label' or 'residue_name' column in '{residues_file}'.")

    output_table = prepare_output_table(cav_residues, res_label_name)

    ## write_csv(output_table, pdb_name, output_dir)
    write_xlsx(output_table, pdb_name, output_dir)


    return cav_residues, res_label_name


def prepare_output_table(cav_residues, res_label_name):
    """
    Prepares the output table for .csv and .xlsx files.
    Args:
        cav_residues (dict): Dictionary with cavity numbers as keys and residue IDs as values.
        res_label_name (dict): Dictionary with residue labels as keys and residue names as values.
    Returns:
        list: List of dictionaries, each representing a row in the output table.
    """
    output_table = []

    for cavity_number, residue_ids_str in cav_residues.items():
        residue_ids = residue_ids_str.split()  # Split by spaces

        for residue_id in residue_ids:
            chain, seq_id = residue_id.split('_')  # Split by '_'
            aa = res_label_name.get(seq_id, 'Unknown')  # Look up AA in res_label_name

            row = {
                "Cavity Number": cavity_number,
                "Chain": chain,
                "Seq ID": seq_id,
                "AA": aa
            }
            output_table.append(row)

    return output_table


def write_csv(output_table, pdb_name, output_dir):
    """
    Writes the output table to a .csv file.
    Args:
        output_table (list): List of dictionaries representing the output table.
        pdb_name (str): Name of the PDB file (used for the output filename).
        output_dir (str): Directory where the output file will be saved.
    """

    # Create output subfolder
    output_or_subfolder = os.path.join(os.getcwd(), output_dir, pdb_name)
    os.makedirs(output_or_subfolder, exist_ok=True)

    output_filename = FileNamer.get_residues_name(pdb_name, MethodType.P2RK) + ".csv"
    output_path = os.path.join(output_or_subfolder, output_filename)

    with open(output_path, mode='w', newline='') as csvfile:
        fieldnames = ["Cavity Number", "Chain", "Seq ID", "AA"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(output_table)

    logger.info(f"Output table saved to '{output_path}' at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def write_xlsx(output_table, pdb_name, output_dir):
    """
    Writes the output table to an .xlsx file with multiple sheets.
    Args:
        output_table (list): List of dictionaries representing the output table.
        pdb_name (str): Name of the PDB file (used for the output filename).
        output_dir (str): Directory where the output file will be saved.
    """
    # Create output subfolder
    output_or_subfolder = os.path.join(os.getcwd(), output_dir, pdb_name)
    os.makedirs(output_or_subfolder, exist_ok=True)

    # Use the same naming convention as for the CSV file
    output_filename = FileNamer.get_residues_name(pdb_name, MethodType.P2RK) + ".xlsx"
    output_path = os.path.join(output_or_subfolder, output_filename)

    # Create a DataFrame from the output_table
    df = pd.DataFrame(output_table)

    # Create a dictionary to hold DataFrames for each cavity number
    sheets = {}
    for cavity_number in df["Cavity Number"].unique():
        sheet_name = f"Cavity {cavity_number}"
        sheets[sheet_name] = df[df["Cavity Number"] == cavity_number]

    # Write to Excel with multiple sheets
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, sheet_df in sheets.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

    logger.info(f"Output table saved to '{output_path}' at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    config = load_config()
    chrome_driver_path = config['chrome_driver_path']
    print("Driver path: " + chrome_driver_path)
    input_dir = config['input_dir']
    output_dir = config['output_dir']
    pdb_input = config['pdb_input']
    process_p2rank_local_output(pdb_input, config)
    #only_unzip_and_process()
