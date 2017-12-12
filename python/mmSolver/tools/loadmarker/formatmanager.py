"""
A manager class for registering new marker file formats.
"""

# module level manager, stores an instance of 'FormatManager'.
__format_manager = None


class FormatManager(object):
    def __init__(self):
        self.__formats = {}

    def register_format(self, class_obj):
        if str(class_obj) not in self.__formats:
            self.__formats[str(class_obj)] = class_obj
        return True

    def get_formats(self):
        format_list = []
        for key in self.__formats:
            format = self.__formats[key]
            format_list.append(format)
        return format_list


def get_format_manager():
    global __format_manager
    if __format_manager is None:
        __format_manager = FormatManager()
    return __format_manager


