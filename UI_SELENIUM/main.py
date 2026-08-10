import argparse

from configparser import SectionProxy
from datetime import datetime
import logging

from castpfold_to_csv import run_castpfold
from cavity_plus_to_csv import run_cavity_plus
from prankweb_local_out_to_csv import process_p2rank_local_output
from pupp_out_to_csv import  process_pupp_out_directory
from utils import load_config
import os

# Set a specific logger for the project
logger = logging.getLogger(__name__)

# Color formatting class for console output
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[37m",     # Gray
        logging.INFO: "\033[0m",       # Default
        logging.WARNING: "\033[33m",   # Yellow
        logging.ERROR: "\033[31m",     # Red
        logging.CRITICAL: "\033[41m",  # Red background
    }

    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)

        if record.levelno >= logging.WARNING:
            msg = f"{record.levelname}: {record.getMessage()}"
        else:
            msg = record.getMessage()

        return f"{color}{msg}{self.RESET}"
# End of ColorFormatter class



def get_pdb_files(input_directory: str) -> list[str]:
    """
    Returns a list of .pdb file names in the specified directory.

    Args:
        input_directory (str): The directory to search for .pdb files.

    Returns:
        list[str]: A list of .pdb file names.
    """
    pdb_files = []
    for filename in os.listdir(input_directory):
        if filename.endswith('.pdb'):
            pdb_files.append(filename)
    return pdb_files

def run_4_predictions(pdb_files: list[str], config: SectionProxy) -> None:
    # Processing output files of pacupp JMOL script
    # It is expected, that java JMOL pacupp has been run prior to this python script

    logger.info(f"Expecting that java pacupp has already completed. Processing pacupp output files for {pdb_files}  at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pacupp_python_feedup = config['pacupp_python_feedup']

    process_pupp_out_directory(pacupp_python_feedup, config)
    process_p2rank_local_output(pdb_files, config)

    #raise Exception("Temporary stop")

    for pdb_file in pdb_files:
        logger.info("")
        logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info(f'Running 4 predictions for {pdb_file}')
        logger.info(f"Starting CastPFold for {pdb_file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        run_castpfold(pdb_file, config)

        logger.info(f"Starting CavityPlus for {pdb_file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        run_cavity_plus(pdb_file, config)
        logger.info(f"Starting PrankWev for {pdb_file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # !!!! run_prankweb(pdb_file, config) replaced by local p2rank run, see above

        logger.info(f"Completing 4predictions for {pdb_file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    pass



def main(rerun_prediction: str = None) -> None:
    # Setting logger and color logging fot console
    timestamp = datetime.now().strftime("%y%m%d_%H%M")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("main.py dir: ", script_dir)
    log_dir = f"{script_dir}/../logs"
    os.makedirs(log_dir, exist_ok=True)

    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter())

    file_handler = logging.FileHandler(f"{log_dir}/main_{timestamp}.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            handler, file_handler
        ]
    )
    # end of logger settings


    logger.info(f"Starting main.py script... at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    config = load_config()
    logging.info(f"DEFAULT config: {config.items()}")
    input_dir = config['input_dir']
    pdb_files = get_pdb_files(input_dir)
    if(len(pdb_files) <1 ):
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"No input .pdb files found in {input_dir} \n no new cavity residues files for any method are expected")

    if rerun_prediction is None:
        run_4_predictions(pdb_files, config)
    elif rerun_prediction == "cspf":
        for pdb_file in pdb_files:
            logger.info(f'Re-Running only CASTpFold for {pdb_file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
            run_castpfold(pdb_file, config)
    elif rerun_prediction == "cvpl":
        for pdb_file in pdb_files:
            logger.info(f'Re-Running  only CavityPlus for {pdb_file} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
            run_cavity_plus(pdb_file, config)
    elif rerun_prediction == "p2rk":
        logger.info(f'Re-processing  PrankWeb local output for {", ".join(pdb_files)}\n at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
        process_p2rank_local_output (pdb_files, config)
    elif rerun_prediction == "pupp":
        logger.info(f"Skipping web predictions. Only processing pacupp output files. at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pacupp_python_feedup = config['pacupp_python_feedup']
        process_pupp_out_directory(pacupp_python_feedup, config)
    else:
        raise ValueError(f"Invalid --rerun-prediction option: {rerun_prediction}. Allowed values: cspf, cvpl, p2rk, pupp")



if __name__ == '__main__':
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Run predictions or reprocess specific steps.")
    parser.add_argument(
        "-r", "--rerun-prediction",
        choices=["cspf", "cvpl", "p2rk", "pupp"],
        help="Specify which prediction to rerun: cspf (CASTpFold), cvpl (CavityPlus), p2rk (PrankWeb), pupp (process pacupp output only)."
    )
    args = parser.parse_args()

    # Call the main function with the parsed argument
    main(args.rerun_prediction)

    logger.info(f"End of main.py script... at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

