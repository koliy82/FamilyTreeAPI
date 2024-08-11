import os
from tempfile import NamedTemporaryFile


class TempFile:
    def __init__(self, suffix=None, prefix=None, dir=None, delete=False):
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir
        self.path = None
        self.delete = delete

    def __enter__(self):
        """Creates a temporary file, save and returns the path to it."""
        self.temp_file = NamedTemporaryFile(suffix=self.suffix, prefix=self.prefix, dir=self.dir, delete=self.delete)
        self.path = self.temp_file.name
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Closes the temporary file and removes it."""
        try:
            if self.temp_file:
                self.temp_file.close()
            if self.path and os.path.exists(self.path):
                os.remove(self.path)
        except Exception as e:
            print(f"Error while closing or removing temp file: {e}")

    def read(self):
        """Reads the content of the temporary file."""
        with open(self.path, 'rb') as f:
            return f.read()
