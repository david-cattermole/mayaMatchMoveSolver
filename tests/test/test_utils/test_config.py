"""
Test functions for API utils module.
"""

import unittest

import test.test_utils.utilsutils as test_utils
import mmSolver.utils.config as utils_config


# @unittest.skip
class TestConfig(test_utils.UtilsTestCase):
    """
    Test config module.
    """

    def test_class_usage1(self):
        config = utils_config.get_config('test.json')
        value = config.get_value('myVar')
        assert value == None
        value = config.set_value('myVar')
        return

    def test_class_usage2(self):
        config = utils_config.get_config('test.json')
        config.set_autoread(True)
        config.set_autowrite(True)
        value = config.get_value('myVar')
        assert value == None
        value = config.set_value('myVar')
        return

    def test_class_usage3(self):
        config = utils_config.get_config('test.json')
        config.set_autoread(False)
        config.set_autowrite(False)
        config.read()
        value = config.get_value('myVar')
        assert value == None
        config.set_value('myVar', 42)
        config.write()
        return

    def test_get_dirs(self):
        name = 'MMSOLVER_CONFIG_PATH'
        dir_list = utils_config.get_dirs(name)
        assert isinstance(dir_list, list)
        assert len(dir_list) > 0
        return
    
    def test_function_usage1(self):
        path = self.get_data_path('config')
        dir_list = [path]
        file_path = utils_config.find_path('test.json', dir_list)

        data = utils_config.read_data(file_path)
        value = utils_config.get_value(data, 'myVar')
        new_value = 42
        assert value != new_value
        utils_config.set_value(data, 'myVar', new_value)
        utils_config.write_data(data, file_path)

        data2 = utils_config.read_data(file_path)
        assert data != data2
        value2 = utils_config.get_value(data, 'myVar')
        assert value2 == new_value
        utils_config.set_value(data, 'myVar', value)
        return


if __name__ == '__main__':
    prog = unittest.main()
