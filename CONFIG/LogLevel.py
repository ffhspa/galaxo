class LogLevel:
    INFO = "INFO"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    WARNING = "WARNING"

    @classmethod
    def get_level_names(cls):
        return ['INFO', 'ERROR', 'DEBUG', 'WARNING']
