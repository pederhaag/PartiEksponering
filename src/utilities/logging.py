def log(obj, message):
    if obj.log_mode:
        print(type(obj).__name__ + ": " + message)

def verbose(obj, message):
    if obj.log_mode and obj.verbose:
        print(type(obj).__name__ + ": " + message)
