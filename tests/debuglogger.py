import logging


def setup_logging() -> logging.Logger:
    # Create the logger for 'crudclient'
    logger = logging.getLogger("crudclient")

    # Set the logger's level to DEBUG to capture all levels of logs
    logger.setLevel(logging.DEBUG)

    # Define a standard formatter for the log messages
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create and configure the FileHandler to log to 'error.log'
    file_handler = logging.FileHandler("/workspace/logs/error.log")
    file_handler.setLevel(logging.INFO)  # Log only INFO level and above to the file
    file_handler.setFormatter(formatter)

    # Add the FileHandler to the logger
    logger.addHandler(file_handler)

    # Optionally, you can also add a StreamHandler to output logs to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # Log all levels to the console
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
