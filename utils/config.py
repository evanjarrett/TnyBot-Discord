import configparser
import os


class Config:
    def __init__(self, file, section):
        self.file = file
        self.section = section

        self.config = configparser.RawConfigParser()

        if not os.path.isfile(self.file):
            self.config.add_section(self.section)
            self._write()

    def get(self, option):
        self.config.read(self.file)
        return self.config.get(self.section, option)

    def get_as_list(self, option):
        return self.get(option).split(',')

    def get_all(self):
        self.config.read(self.file)
        return self.config.options(self.section)

    def save(self, option, value):
        self.config.set(self.section, option, value)
        self._write()

    def append(self, option, value):
        try:
            current_val = self.get(option)
        except configparser.NoOptionError:
            self.save(option, value)
            return

        if current_val is None:
            self.save(option, value)
            return

        if value in current_val.split(","):
            return

        value = current_val + "," + value
        self.save(option, value)

    def truncate(self, option, value):
        try:
            current_val = self.get(option)
        except configparser.NoOptionError:
            return

        if current_val is None:
            return

        if "," in current_val:
            values = current_val.split(",")
            if value in values:
                values.remove(value)
                self.save(option, ",".join(values))
        else:
            self.delete(option)

    def delete(self, option):
        self.config.read(self.file)
        deleted = self.config.remove_option(self.section, option)
        self._write()
        return deleted

    def has(self, option):
        self.config.read(self.file)
        return self.config.has_option(self.section, option)

    def contains(self, option, search):
        try:
            val = self.get(option)
            if val is None:
                return False
            if search in val.split(','):
                return True
        except configparser.NoOptionError:
            return False

    def _write(self):
        with open(self.file, 'w+') as configfile:
            self.config.write(configfile)
