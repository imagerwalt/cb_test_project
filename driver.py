import argparse
import sys

from src.services.log_collection import LogCollectionService

if __name__ == '__main__':
    if len(sys.argv) == 3 or len(sys.argv) == 4:
        filename = sys.argv[1]
        num_of_messages = sys.argv[2]
        filter_keyword = sys.argv[3] if len(sys.argv) == 4 else None
    elif sys.stdin.isatty():
        filename = input("Please enter the filename:")
        num_of_messages = input("Please enter the number of logs:")
        filter_keyword = input("Please enter the keyword (optional, press enter to skip):")
        need_output = input("Would you like to output as log file? If so, please specify a filename (optional)")

    if filter_keyword == '':
        filter_keyword = None
    num_of_messages = int(num_of_messages)

    log_results = LogCollectionService.log_reader(filename, num_of_messages, filter_keyword)
    if need_output:
        output_file = open(need_output, mode='w')
        for result in log_results['logs']:
            output_file.write(result + '\n')
    else:
        for result in log_results['logs']:
            print(result)