import argparse
import configparser
from datetime import datetime
import logging
import os
import shutil
from UI_SELENIUM.file_namer import MethodType

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
    clean_before_copy: bool = False
) -> None:
    """
    Verify XLSX outputs per OR_NAME (case-insensitive) and copy
    OR_NAME folders and PDB files into the PyMOL input directory.

    Also writes a summary.txt file with:
    - number of .pdb input files
    - number of OR_NAME entries with missing XLSX methods
    - detailed missing methods per OR_NAME
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
            raise NotADirectoryError(f"{label} does not exist or is not a directory: {path}")

    os.makedirs(pymol_input_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Optional cleanup
    # ------------------------------------------------------------------
    if clean_before_copy:
        logger.info(f"Cleaning directory before copy: {pymol_input_dir}")
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
    pdb_files = [f for f in input_files if f.lower().endswith(".pdb")]
    X = len(pdb_files)

    # ------------------------------------------------------------------
    # 1. Collect OR_NAME directories
    # ------------------------------------------------------------------
    or_names = [
        name for name in os.listdir(selenium_output_dir)
        if name != "OLD_DATA"
        and os.path.isdir(os.path.join(selenium_output_dir, name))
    ]

    # ------------------------------------------------------------------
    # 2. Verify XLSX files per OR_NAME
    # ------------------------------------------------------------------
    Z = 0
    missing_dict = {}  # <-- NEW

    for or_name in or_names:
        or_dir = os.path.join(selenium_output_dir, or_name)

        xlsx_files = [
            f for f in os.listdir(or_dir)
            if f.lower().endswith(".xlsx")
        ]

        missing_methods = []  # <-- collect per OR_NAME

        for method in MethodType:
            found = any(
                f.lower().startswith(or_name.lower())
                and method.value in f.lower()
                for f in xlsx_files
            )

            if not found:
                missing_methods.append(method.value)  # or method.name if preferred
                logger.warning(
                    f"Missing XLSX file for OR_NAME='{or_name}', "
                    f"MethodType='{method.name}', "
                    f"!!!!!!!! CONSENSUS file cannot be built for {or_name}!!!!"
                )

        if missing_methods:
            Z += 1
            missing_dict[or_name] = missing_methods  # <-- store result

    # ------------------------------------------------------------------
    # 3. Copy OR_NAME directories
    # ------------------------------------------------------------------
    for or_name in or_names:
        src_dir = os.path.join(selenium_output_dir, or_name)
        dst_dir = os.path.join(pymol_input_dir, or_name)

        if os.path.exists(dst_dir):
            logger.info(f"+++++ Directory already exists and will be overwritten: {dst_dir}")
            shutil.rmtree(dst_dir)

        shutil.copytree(src_dir, dst_dir)

    # ------------------------------------------------------------------
    # 4. Copy {OR_NAME}.pdb
    # ------------------------------------------------------------------
    for or_name in or_names:
        pdb_found = next(
            (f for f in input_files if f.lower() == f"{or_name.lower()}.pdb"),
            None
        )

        if pdb_found is None:
            logger.warning(
                f"!!!!!!! Missing PDB file for OR_NAME='{or_name}', PYMOL script won't work for it"
            )
            continue

        shutil.copy2(
            os.path.join(selenium_input_dir, pdb_found),
            os.path.join(pymol_input_dir, or_name, pdb_found)
        )

    # ------------------------------------------------------------------
    # 5. Write 4methods_summary.txt
    # ------------------------------------------------------------------
    timestamp = datetime.now().strftime("%H%M")
    parent_dir = os.path.dirname(pymol_input_dir)
    summary_path = os.path.join(parent_dir, f"4methods_summary_{timestamp}.txt")


    with open(summary_path, "w") as f:
        f.write(f"The job included {X} .pdb files\n")
        f.write(f"{Z} files have missing methods\n")

        if missing_dict:
            f.write("\nDetails:\n")
            for or_name, methods in missing_dict.items():
                methods_str = ", ".join(methods)
                f.write(f"{or_name}: missing [{methods_str}]\n")

    logger.info(f"Summary written to: {summary_path}")



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

    args = parser.parse_args()
    clean_before = args.clean_before_copy

    verify_and_copy(selenium_input_dir, selenium_output_dir, pymol_input_dir,
                    clean_before_copy=clean_before)
    logger.info("===============================================================================================")
    logger.info(f"Verify and copy from {selenium_input_dir}, {selenium_output_dir} -> {pymol_input_dir} completed")
    logger.info("===============================================================================================")


if __name__ == '__main__':
    main()