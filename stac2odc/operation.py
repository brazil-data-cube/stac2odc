

def load_user_defined_function(function_name: str, module_file: str):
    """Function to load arbitrary functions

    Args:
        function_name (str): name of function to load from function_file
        module_file (str): file module where function is defined
    Returns:
        function loaded from file
    """

    import types
    import importlib.machinery

    loader = importlib.machinery.SourceFileLoader('user_defined_module', module_file)
    module = types.ModuleType(loader.name)
    loader.exec_module(module)

    return getattr(module, function_name)
