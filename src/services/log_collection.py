import os
import re
import time
from src.constants import TIMEOUT


class LogCollectionService(object):
    @classmethod
    def log_reader(cls, filename, num_of_lines, filter_keyword=None, timeout=TIMEOUT):
        seek_position = cls._seek_position(filename)
        for line, timer, timed_out, seek_position in cls._read_log_generator(filename, num_of_lines, filter_keyword, timeout, seek_position):
            yield line + '\n'


    @staticmethod
    def _seek_position(filename):
        with open(filename, errors='ignore') as log_file:
            log_file.seek(0, os.SEEK_END)
            return log_file.tell()


    @classmethod
    def _read_log_generator(cls, filename, num_of_lines, filter_keyword, timeout, position):
        with open(filename, errors='ignore') as log_file:
            current_line = 0
            log_file.seek(0, os.SEEK_END)
            line = ''
            start_time = time.time()
            timeout_timestamp = timeout + start_time
            has_timed_out = False
            while position >= 0:
                cur_time = time.time()
                timer = cur_time - start_time

                if cur_time > timeout_timestamp:
                    has_timed_out = True
                    yield None, timer, has_timed_out, position
                    break

                log_file.seek(position)
                next_char = log_file.read(1)
                if next_char == "\n":
                    new_line = line[::-1]
                    found_line = cls._lookup(new_line, filter_keyword)
                    if found_line:
                        yield new_line, timer, has_timed_out, position
                        current_line += 1
                        if current_line == num_of_lines:
                            break
                    line = ''
                else:
                    line += next_char
                position -= 1

                # if it goes to the top of the file (first character), output it,
                # since it will be outside of the while loop
                if position == -1:
                    new_line = line[::-1]
                    found_line = cls._lookup(new_line, filter_keyword)
                    if found_line:
                        yield new_line, timer, has_timed_out, position

    @staticmethod
    def _lookup(line, keyword):
        if re.match(r'\S+', line):
            if not keyword:
                return True
            result = re.search(keyword, line, re.IGNORECASE)
            return result
