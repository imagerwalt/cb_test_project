import os
import re
import time
import json
from src.constants import TIMEOUT, CHAR_READ


class LogCollectionService(object):
    @classmethod
    def log_reader(cls, filename, num_of_lines, filter_keyword=None, timeout=TIMEOUT):
        for line, timer in cls._read_log_generator(filename, num_of_lines, filter_keyword, timeout):
            yield cls.form_output(line, timer) + '\n'

    @staticmethod
    def form_output(line, timer):
        return json.dumps({'log': line, 'timer': timer})

    @classmethod
    def _read_log_generator(cls, filename, num_of_lines, filter_keyword, timeout):
        with open(filename, errors='ignore') as log_file:
            current_line = 0
            log_file.seek(0, os.SEEK_END)
            position = log_file.tell()
            line = ''
            start_time = time.time()
            timeout_timestamp = timeout + start_time

            while position >= 0:
                cur_time = time.time()
                timer = cur_time - start_time
                if cur_time > timeout_timestamp:
                    break

                log_file.seek(position)
                next_chars = log_file.read(CHAR_READ)
                newline_loc = next_chars.find("\n")
                if newline_loc >= 0:
                    line = next_chars[newline_loc + 1::] + line
                    found_line = cls._lookup(line, filter_keyword)
                    if found_line:
                        yield line, timer
                        current_line += 1
                        if current_line == num_of_lines:
                            break
                    line = next_chars[0:newline_loc]
                else:
                    line = next_chars + line

                position -= CHAR_READ

                # if it goes to the top of the file (first batch of character), output it,
                # since it will be outside of the while loop
                if position < 0:
                    # read the remaining characters left unread
                    log_file.seek(0)
                    next_chars = log_file.read(CHAR_READ)
                    remaining_chars = CHAR_READ + position

                    line = next_chars[0:remaining_chars] + line
                    found_line = cls._lookup(line, filter_keyword)
                    if found_line:
                        yield line, timer

    @staticmethod
    def _lookup(line, keyword):
        if re.match(r'\S+', line):
            if not keyword:
                return True
            result = re.search(keyword, line, re.IGNORECASE)
            return result
