"""
Test functions for API utils module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil
import unittest

import test.test_utils.utilsutils as test_utils
import mmSolver.utils.config as utils_config


# @unittest.skip
class TestConfig(test_utils.UtilsTestCase):
    """
    Test config module.
    """

    def test_function_usage1(self):
        original_name = 'test01.json'
        name = 'test01_function_usage1.json'
        path = self.get_data_path('config')
        dir_list = [path]

        src = os.path.join(path, original_name)
        dst = os.path.join(path, name)
        shutil.copy2(src, dst)

        file_path = utils_config.find_path(name, dir_list)
        data = utils_config.read_data(file_path)
        value = utils_config.get_value(data, 'myVar')
        new_value = 42
        assert value != new_value
        new_data = utils_config.set_value(data, 'myVar', new_value)
        utils_config.write_data(new_data, file_path)

        data2 = utils_config.read_data(file_path)
        assert data != data2
        assert new_data == data2
        value2 = utils_config.get_value(data2, 'myVar')
        assert value2 == new_value
        new_data2 = utils_config.set_value(data2, 'myVar2', value2 + 1)
        utils_config.write_data(new_data2, file_path)
        return

    def test_set_value(self):
        # one level
        data1 = {}
        key = 'myVar'
        value = 42
        new_data1 = utils_config.set_value(data1, key, value)
        assert new_data1.get(key) == value

        # two levels
        data2 = {}
        key = 'myVar/mySubVar'
        value = 42
        new_data2 = utils_config.set_value(data2, key, value)
        assert new_data2.get('myVar') == {'mySubVar': value}
        assert new_data2.get('myVar').get('mySubVar') == value

        # three levels
        data3 = {}
        key = 'key/sub/subsub'
        value = 42
        new_data3 = utils_config.set_value(data3, key, value)
        d1 = new_data3.get('key')
        assert d1 == {'sub': {'subsub': value}}
        d2 = d1.get('sub')
        assert d2 == {'subsub': value}
        d3 = d2.get('subsub')
        assert d3 == value

        # overwrite an existing value.
        key = 'myVar/mySubVar'
        value = 42
        new_data4 = utils_config.set_value(data1, key, value)
        assert new_data4.get('myVar') == {'mySubVar': value}
        assert new_data4.get('myVar').get('mySubVar') == value
        assert new_data2 == new_data4

        # Add a new key to an existing data.
        key = 'myNewVar/myNewSubVar'
        value = 42
        new_data5 = utils_config.set_value(new_data2, key, value)
        assert new_data5.get('myVar') == {'mySubVar': value}
        assert new_data5.get('myVar').get('mySubVar') == value
        assert new_data5.get('myNewVar') == {'myNewSubVar': value}
        assert new_data5.get('myNewVar').get('myNewSubVar') == value

        # Merge a new key into an existing data.
        key = 'myVar/myNewSubVar'
        value = 42
        new_data6 = utils_config.set_value(new_data5, key, value)
        assert new_data6.get('myNewVar') == {'myNewSubVar': value}
        assert new_data6.get('myNewVar').get('myNewSubVar') == value
        assert new_data6.get('myVar') == {'mySubVar': value, 'myNewSubVar': value}
        assert new_data6.get('myVar').get('mySubVar') == value
        assert new_data6.get('myVar').get('myNewSubVar') == value
        return

    def test_class_usage1(self):
        """
        The easiest read and write functions using the Config class.

        Using default Auto-Read/Write values.
        """
        original_name = 'general.json'
        name = 'general_class_usage1.json'
        path = self.get_data_path('config')
        dir_list = [path]

        src = os.path.join(path, original_name)
        dst = os.path.join(path, name)
        shutil.copy2(src, dst)

        config = utils_config.get_config(name, search=dir_list)
        assert config is not None
        value = config.get_value('myVar')
        assert value is None

        new_value = 42
        config.set_value('myVar', new_value)

        value = config.get_value('myVar')
        assert value == new_value
        return

    def test_class_usage2(self):
        """
        Read and write functions using the Config class.

        Forcing Auto-Read/Write to be ON.
        """
        original_name = 'general.json'
        name = 'general_class_usage2.json'
        path = self.get_data_path('config')
        dir_list = [path]

        src = os.path.join(path, original_name)
        dst = os.path.join(path, name)
        shutil.copy2(src, dst)

        config = utils_config.get_config(name, search=dir_list)
        assert config is not None
        config.set_autoread(True)
        config.set_autowrite(True)
        value = config.get_value('myVar')
        assert value is None

        new_value = 42
        config.set_value('myVar', new_value)

        value = config.get_value('myVar')
        assert value == new_value
        return

    def test_class_usage3(self):
        """
        Read and write functions using the Config class.

        Turn Auto-Read/Write OFF.
        """
        original_name = 'general.json'
        name = 'general_class_usage3.json'
        path = self.get_data_path('config')
        dir_list = [path]

        src = os.path.join(path, original_name)
        dst = os.path.join(path, name)
        shutil.copy2(src, dst)

        config = utils_config.get_config(name, search=dir_list)
        assert config is not None
        config.set_autoread(False)
        config.set_autowrite(False)
        config.read()
        value = config.get_value('myVar')
        assert value is None

        new_value = 42
        config.set_value('myVar', new_value)
        config.write()

        config.read()
        value = config.get_value('myVar')
        assert value == new_value
        return

    def test_class_key_hierarchy(self):
        """
        Read and write functions with hierarchy of key values using the
        Config class.

        Using default Auto-Read/Write values.
        """
        original_name = 'general.json'
        name = 'general_class_key_hierarchy.json'
        path = self.get_data_path('config')
        dir_list = [path]

        src = os.path.join(path, original_name)
        dst = os.path.join(path, name)
        shutil.copy2(src, dst)

        config = utils_config.get_config(name, search=dir_list)
        assert config is not None
        key = 'key/subkey/subsubkey'
        value = config.get_value(key)
        assert value is None

        new_value = 42
        config.set_value(key, new_value)

        value = config.get_value(key)
        assert value == new_value

        config.write()
        return

    def test_get_dirs(self):
        name = 'MMSOLVER_CONFIG_PATH'
        dir_list = utils_config.get_dirs(name)
        assert isinstance(dir_list, list)
        assert len(dir_list) > 0
        return


if __name__ == '__main__':
    prog = unittest.main()
