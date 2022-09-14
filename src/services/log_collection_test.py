import pytest
from mock_open import MockOpen
from unittest import mock
import time

from src.services.log_collection import LogCollectionService


@pytest.fixture
def fixture_generated_log():
    return [
        ('test_log_1', float(1665544332211), False),
        ('test_log_2', float(1665544332212), False),
        ('test_log_3', float(1665544332213), False),
        ('test_log_4', float(1665544332214), False),
        ('test_log_5', float(1665544332215), False),
    ]


@pytest.fixture
def fixture_raw_log():
    return "test_log_1aaa\ntest_log_2aaa\ntest_log_3bbb\ntest_log_4aaa\ntest_log_5ccc\n"


@mock.patch('os.path.getsize', return_value=13579)
@mock.patch.object(LogCollectionService, '_read_log_generator')
def test_log_reader(mock_log_generator, mock_filesize, fixture_generated_log):
    mock_log_generator.return_value = iter(fixture_generated_log)

    results = LogCollectionService.log_reader('some_file.log', 5)
    assert results['logs'] == ['test_log_1',
                               'test_log_2',
                               'test_log_3',
                               'test_log_4',
                               'test_log_5']
    assert results['count'] == 5
    assert results['filesize'] == 13579
    assert results['query_time'] == float(1665544332215)


@mock.patch('os.path.getsize', return_value=13579)
@mock.patch.object(LogCollectionService, '_read_log_generator')
def test_log_reader_timeout(mock_log_generator, mock_filesize, fixture_generated_log):
    fixture_generated_log.append((None, 1665544332216, True))
    mock_log_generator.return_value = iter(fixture_generated_log)

    results = LogCollectionService.log_reader('some_file.log', 5)
    assert results['logs'] == ['test_log_1',
                               'test_log_2',
                               'test_log_3',
                               'test_log_4',
                               'test_log_5']
    assert results['count'] == 5
    assert results['filesize'] == 13579
    assert results['query_time'] == float(1665544332216)
    assert results['message'] == "Timeout, partial results listed"


@mock.patch.object(time, 'time', return_value=float(0))
def test__read_log_generator(mock_time, fixture_raw_log, fixture_generated_log):
    mock_open_file = MockOpen(read_data=fixture_raw_log)
    with mock.patch('builtins.open', mock_open_file):
        results = LogCollectionService._read_log_generator('test', 3, None, 60)
        result_list = list(results)
        assert result_list == [('test_log_5ccc', float(0), False),
                               ('test_log_4aaa', float(0), False),
                               ('test_log_3bbb', float(0), False)]


@mock.patch.object(time, 'time', return_value=float(0))
def test__read_log_generator_read_last_result(mock_time, fixture_raw_log, fixture_generated_log):
    mock_open_file = MockOpen(read_data=fixture_raw_log)
    with mock.patch('builtins.open', mock_open_file):
        results = LogCollectionService._read_log_generator('test', 5, None, 60)
        result_list = list(results)
        assert result_list == [('test_log_5ccc', float(0), False),
                               ('test_log_4aaa', float(0), False),
                               ('test_log_3bbb', float(0), False),
                               ('test_log_2aaa', float(0), False),
                               ('test_log_1aaa', float(0), False)]


def test__read_log_generator_real_log():
    real_file = '../../linux.log'
    results = LogCollectionService._read_log_generator(real_file, 2000, None, 60)
    result_list = list(results)
    assert len(result_list) == 2000
    ref_list = list()
    with open(real_file, errors='ignore') as ref_file:
        for num, line in enumerate(ref_file):
            ref_list.append((num, line.strip()))
        assert result_list[0][0] == ref_list[-1][1]
        ref_length = len(ref_list)
        assert result_list[1999][0] == ref_list[ref_length - 2000][1]


@mock.patch.object(time, 'time', return_value=float(0))
def test__read_log_generator_search(mock_time, fixture_raw_log, fixture_generated_log):
    mock_open_file = MockOpen(read_data=fixture_raw_log)
    with mock.patch('builtins.open', mock_open_file):
        results = LogCollectionService._read_log_generator('test', 5, 'aaa', 60)
        result_list = list(results)
        assert result_list == [('test_log_4aaa', float(0), False),
                               ('test_log_2aaa', float(0), False),
                               ('test_log_1aaa', float(0), False)]


# todo: to be refined
@mock.patch.object(time, 'time')
def test__read_log_generator_timeout(mock_time, fixture_raw_log, fixture_generated_log):
    mock_time.side_effect = list(range(0, 1000))
    real_file = '../../linux.log'
    results = LogCollectionService._read_log_generator(real_file, 2000, None, 600)
    result_list = list(results)
    assert result_list[-1][0] is None
    assert result_list[-1][2] is True
