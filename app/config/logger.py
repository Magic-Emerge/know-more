import logging
import json
import os
from logging.handlers import RotatingFileHandler
import argparse


class JsonFormatter(logging.Formatter):
    def __init__(self):
        super(JsonFormatter, self).__init__()

    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'filename': record.filename,
            'lineno': record.lineno,
            'funcname': record.funcName,
            'exception': record.exc_info
        }
        return json.dumps(log_record)


def get_logger(log_file_path="logs/app.log", max_size_mb=5, backup_count=3):
    log_dir_path = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir_path):
        os.makedirs(log_dir_path)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    max_bytes = max_size_mb * 1024 * 1024
    fh = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
    fh.setLevel(logging.DEBUG)

    json_formatter = JsonFormatter()
    fh.setFormatter(json_formatter)

    logger.addHandler(fh)

    return logger


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CalfAI App')
    parser.add_argument('--log-file', type=str, default='logs/app.log',
                        help='Path to the log file')
    parser.add_argument('--max-size-mb', type=int, default=5,
                        help='Maximum size of the log file in megabytes')
    parser.add_argument('--backup-count', type=int, default=3,
                        help='Number of backup files to keep')

    args = parser.parse_args()

    logger = get_logger(args.log_file, args.max_size_mb, args.backup_count)