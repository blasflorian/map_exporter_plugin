import os


def get_plugin_path():
    """ Gets the current path to plugin directory
        
        :returns: path to plugin directory
        :rtype: str
    """
    return os.path.dirname(os.path.realpath(__file__))