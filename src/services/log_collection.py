import os
import re
import time
from src.constants import TIMEOUT


class LogCollectionService(object):
    @classmethod
    def log_reader(cls, filename, num_of_lines, filter_keyword=None, timeout=TIMEOUT):
        log_list = list()
        results = dict()
        timer = float(0)
        for line, timer, timed_out in cls._read_log_generator(filename, num_of_lines, filter_keyword, timeout):
            if timed_out:
                results['message'] = "Timeout, partial results listed"
            else:
                log_list.append(line)

        results['logs'] = log_list
        results['count'] = len(log_list)
        results['filesize'] = os.path.getsize(filename)
        results['query_time'] = timer
        return results

    @classmethod
    def _read_log_generator(cls, filename, num_of_lines, filter_keyword, timeout):
        with open(filename, errors='ignore') as log_file:
            current_line = 0
            log_file.seek(0, os.SEEK_END)
            line = ''
            position = log_file.tell()
            start_time = time.time()
            timeout_timestamp = timeout + start_time
            has_timed_out = False
            while position >= 0:
                cur_time = time.time()
                timer = cur_time - start_time

                if cur_time > timeout_timestamp:
                    has_timed_out = True
                    yield None, timer, has_timed_out
                    break

                log_file.seek(position)
                next_char = log_file.read(1)
                if next_char == "\n":
                    new_line = line[::-1]
                    found_line = cls._lookup(new_line, filter_keyword)
                    if found_line:
                        yield new_line, timer, has_timed_out
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
                        yield new_line, timer, has_timed_out

    @staticmethod
    def _lookup(line, keyword):
        if re.match(r'\S+', line):
            if not keyword:
                return True
            result = re.search(keyword, line, re.IGNORECASE)
            return result
