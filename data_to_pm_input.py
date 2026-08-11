import argparse
import configparser
from datetime import datetime
import logging
import os
import shutil

from UI_SELENIUM.methods_summary import get_methods_summary

# Set a logger for this very script
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



def verify_and_copy(
    selenium_input_dir: str,
    selenium_output_dir: str,
    pymol_input_dir: str,
    clean_before_copy: bool = False,
    save_after_copy: bool = False
) -> None:
    """
    Verify XLSX outputs per OR_NAME (case-insensitive) and copy
    OR_NAME folders and PDB files into the PyMOL input directory.
    """

    # ------------------------------------------------------------------
    # Sanity checks
    # ------------------------------------------------------------------
    for path, label in [
        (selenium_input_dir, "selenium_input_dir"),
        (selenium_output_dir, "selenium_output_dir"),
        (pymol_input_dir, "pymol_input_dir"),
    ]:
        if not os.path.isdir(path):
            raise NotADirectoryError(
                f"{label} does not exist or is not a directory: {path}"
            )

    os.makedirs(pymol_input_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Optional cleanup
    # ------------------------------------------------------------------
    if clean_before_copy:
        logger.info(
            f"Cleaning directory before copy: {pymol_input_dir}"
        )

        for entry in os.listdir(pymol_input_dir):
            entry_path = os.path.join(pymol_input_dir, entry)

            if os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
            else:
                os.remove(entry_path)

    # ------------------------------------------------------------------
    # Count .pdb input files
    # ------------------------------------------------------------------
    input_files = os.listdir(selenium_input_dir)

    pdb_files = [
        f
        for f in input_files
        if f.lower().endswith(".pdb")
    ]

    X = len(pdb_files)

    # ------------------------------------------------------------------
    # Verify methods and write summary
    # ------------------------------------------------------------------
    parent_dir = os.path.dirname(pymol_input_dir)

    missing_dict = get_methods_summary(
        selenium_output_dir=selenium_output_dir,
        data_lake_dir=parent_dir
    )

    # ------------------------------------------------------------------
    # Collect OR_NAME directories
    # ------------------------------------------------------------------
    or_names = [
        name
        for name in os.listdir(selenium_output_dir)
        if name != "OLD_DATA"
        and os.path.isdir(os.path.join(selenium_output_dir, name))
    ]

    # ------------------------------------------------------------------
    # Copy OR_NAME directories
    # ------------------------------------------------------------------
    for or_name in or_names:
        src_dir = os.path.join(selenium_output_dir, or_name)
        dst_dir = os.path.join(pymol_input_dir, or_name)

        if os.path.exists(dst_dir):
            logger.info(
                f"+++++ Directory already exists and will be overwritten: "
                f"{dst_dir}"
            )
            shutil.rmtree(dst_dir)

        shutil.copytree(src_dir, dst_dir)

    # ------------------------------------------------------------------
    # Move {OR_NAME}.pdb
    # ------------------------------------------------------------------
    for or_name in or_names:
        pdb_found = next(
            (
                f
                for f in input_files
                if f.lower() == f"{or_name.lower()}.pdb"
            ),
            None
        )

        if pdb_found is None:
            logger.warning(
                f"!!!!!!! Missing PDB file for OR_NAME='{or_name}', "
                f"PYMOL script won't work for it"
            )
            continue

        source_path = os.path.join(
            selenium_input_dir,
            pdb_found
        )

        dest_path = os.path.join(
            pymol_input_dir,
            or_name,
            pdb_found
        )

        if save_after_copy:
            shutil.copy2(source_path, dest_path)

            logger.info(
                f"Copied PDB file (save-after-copy enabled): "
                f"{pdb_found} to {dest_path}"
            )

        else:
            if or_name in missing_dict:
                shutil.copy2(source_path, dest_path)

                logger.warning(
                    f"PDB file copied but not moved for OR_NAME='{or_name}' "
                    f"due to missing methods. File: {pdb_found}"
                )
            else:
                shutil.move(source_path, dest_path)

                logger.info(
                    f"Moved PDB file: {pdb_found} to {dest_path}"
                )



def main() -> None:

    # Setting logger and color logging fot console
    timestamp = datetime.now().strftime("%y%m%d_%H%M")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("data_to_pm_input.py dir: ", script_dir)
    log_dir = f"{script_dir}/logs"
    os.makedirs(log_dir, exist_ok=True)

    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter())

    file_handler = logging.FileHandler(f"{log_dir}/log_data_to_pm_{timestamp}.log")
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

    script_dir = os.path.dirname(os.path.abspath(__file__))  # folder of this very script
    logger.info(f"\n!!!!!! Script Data_to_PM_INPUT running at directory: {script_dir} !!!! ")
    selenium_config = configparser.ConfigParser()
    selenium_config_path = os.path.join(script_dir, "UI_SELENIUM/config.ini")
    selenium_config.read(selenium_config_path, encoding="utf-8")

    pymoll_config = configparser.ConfigParser()
    pymoll_config_path = os.path.join(script_dir, "PYMOL_SCRIPTS/pm_config.ini")
    pymoll_config.read(pymoll_config_path, encoding="utf-8")

    data_lake_dir = os.path.join("UI_SELENIUM", selenium_config['DEFAULT']['data_lake_dir'])
    data_lake_dir2 = os.path.join("PYMOL_SCRIPTS", pymoll_config['visualization']['data_lake_dir'])

    selenium_input_dir = os.path.join(data_lake_dir, selenium_config['DEFAULT']['input_dir'])
    selenium_output_dir = os.path.join(data_lake_dir, selenium_config['DEFAULT']['output_dir'])

    pymol_input_dir = os.path.join(data_lake_dir2, pymoll_config['visualization']['pm_input_dir'])

    logger.info("\n\n===============================================================================================")
    logger.info(f"Starting verification and copying: \n {selenium_input_dir}, {selenium_output_dir} -> {pymol_input_dir} completed")
    logger.info("===============================================================================================\n\n")

    parser = argparse.ArgumentParser(
        description="Prepare PyMOL input data from Selenium pipeline output"
    )

    parser.add_argument(
        "-c", "--clean-before-copy",
        action="store_true",
        help="Clean pymol_input_dir before copying"
    )
    parser.add_argument(
        "-s", "--save-after-copy",
        action="store_true",
        help="Always copy PDB files instead of moving them"
    )

    args = parser.parse_args()
    clean_before = args.clean_before_copy
    save_after = args.save_after_copy

    verify_and_copy(selenium_input_dir, selenium_output_dir, pymol_input_dir,
                    clean_before_copy=clean_before, save_after_copy=save_after)
    logger.info("===============================================================================================")
    logger.info(f"Verify and copy from {selenium_input_dir}, {selenium_output_dir} -> {pymol_input_dir} completed")
    logger.info("===============================================================================================")

if __name__ == '__main__':
    main()