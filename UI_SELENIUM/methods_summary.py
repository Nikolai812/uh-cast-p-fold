import configparser
import os
from datetime import datetime
import logging

from .file_namer import MethodType


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




def get_methods_summary(
    selenium_output_dir: str,
    data_lake_dir: str = "."
) -> dict:
    """
    Verify XLSX files per OR_NAME, write a methods summary file,
    and return a dictionary containing missing methods per OR_NAME.

    Args:
        selenium_output_dir: Directory containing OR_NAME subdirectories.
        data_lake_dir: Relative path where the summary file should be written.
                    The path is resolved relative to the directory
                    containing this methods_summary.py file.
                    Default: ".."

    Returns:
        dict: Dictionary containing missing methods per OR_NAME.
              Example:
              {
                  "OR_NAME_1": ["method1", "method2"],
                  "OR_NAME_2": ["method3"]
              }
    """

    # ------------------------------------------------------------------
    # 1. Collect OR_NAME directories
    # ------------------------------------------------------------------
    or_names = [
        name
        for name in os.listdir(selenium_output_dir)
        if name != "OLD_DATA"
        and os.path.isdir(os.path.join(selenium_output_dir, name))
    ]

    # ------------------------------------------------------------------
    # 2. Verify XLSX files per OR_NAME
    # ------------------------------------------------------------------
    missing_dict = {}

    for or_name in or_names:
        or_dir = os.path.join(selenium_output_dir, or_name)

        xlsx_files = [
            f
            for f in os.listdir(or_dir)
            if f.lower().endswith(".xlsx")
        ]

        missing_methods = []

        for method in MethodType:
            found = any(
                f.lower().startswith(or_name.lower())
                and method.value.lower() in f.lower()
                for f in xlsx_files
            )

            if not found:
                missing_methods.append(method.value)

                logger.warning(
                    f"Missing XLSX file for OR_NAME='{or_name}', "
                    f"MethodType='{method.name}', "
                    f"!!!!!!!! CONSENSUS file cannot be built for "
                    f"{or_name}!!!!"
                )

        if missing_methods:
            missing_dict[or_name] = missing_methods

    # ------------------------------------------------------------------
    # 3. Verify/create data lake directory
    # ------------------------------------------------------------------

    summary_dir =  data_lake_dir
    os.makedirs(summary_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # 4. Write summary file
    # ------------------------------------------------------------------
    timestamp = datetime.now().strftime("%H%M")
    summary_path = os.path.join(
        summary_dir,
        f"4methods_summary_{timestamp}.txt"
    )

    with open(summary_path, "w") as f:
        f.write(
            f"The job included the following .pdb files: "
            f"{', '.join(or_names)}\n"
        )
        f.write(
            f"{len(missing_dict)} files have missing methods\n"
        )

        if missing_dict:
            f.write("\nDetails:\n")

            for or_name, methods in missing_dict.items():
                methods_str = ", ".join(methods)
                f.write(
                    f"{or_name}: missing [{methods_str}]\n"
                )

    logger.info(f"Summary written to: {summary_path}")

    return missing_dict

def main():
    # Setting logger and color logging fot console
    timestamp = datetime.now().strftime("%y%m%d_%H%M")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("methods_summary.py dir: ", script_dir)
    log_dir = f"{script_dir}/../logs"
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

    selenium_config = configparser.ConfigParser()
    selenium_config_path = os.path.join(script_dir, "config.ini")
    selenium_config.read(selenium_config_path, encoding="utf-8")

    data_lake_dir = os.path.join(script_dir, selenium_config['DEFAULT']['data_lake_dir'])
    selenium_output_dir = os.path.join(data_lake_dir, selenium_config['DEFAULT']['output_dir'])

    get_methods_summary(
        selenium_output_dir=selenium_output_dir, data_lake_dir=data_lake_dir)

    pass

if __name__ == '__main__':
    main()