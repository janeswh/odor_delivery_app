import sys, os


def resolve_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        # resolved_path = os.path.dirname(os.path.abspath(__file__))
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path
