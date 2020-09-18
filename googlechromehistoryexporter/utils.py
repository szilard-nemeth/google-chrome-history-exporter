import errno
import logging
import os
import shutil
import string
import unicodedata

import humanize
from tabulate import tabulate

LOG = logging.getLogger(__name__)


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    cls.__str__ = __str__
    return cls


class StringUtils:

    @staticmethod
    def replace_special_chars(unistr):
        if not isinstance(unistr, unicode):
            LOG.warning("Object expected to be unicode: " + str(unistr))
            return str(unistr)
        normalized = unicodedata.normalize('NFD', unistr).encode('ascii', 'ignore')
        normalized = normalized.decode('utf-8')
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        valid_title = ''.join(c for c in normalized if c in valid_chars)
        return valid_title


class FileUtils:
    @classmethod
    def ensure_dir_created(cls, dirname):
        """
    Ensure that a named directory exists; if it does not, attempt to create it.
    """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return dirname

    @classmethod
    def ensure_file_exists_and_readable(cls, file):
        LOG.info("Trying to open file %s for reading..", file)
        f = open(file, "r")
        if not f.readable():
            raise ValueError("File {} is not readable".format(file))
        return file

    @staticmethod
    def search_files(basedir, filename):
        result = []
        for dp, dn, filenames in os.walk(basedir):
            for f in filenames:
                if f == filename:
                    result.append(os.path.join(dp, f))
        return result

    @staticmethod
    def copy_file_to_dir(src_file, dst_dir, dst_file_name_func):
        dst_filename = dst_file_name_func(src_file, dst_dir)
        dest_file_path = os.path.join(dst_dir, dst_filename)
        shutil.copyfile(src_file, dest_file_path)
        return dest_file_path

    @classmethod
    def get_file_sizes_in_dir(cls, db_copies_dir):
        files = os.listdir(db_copies_dir)
        result = ""
        for f in files:
            file_path = os.path.join(db_copies_dir, f)
            size = os.stat(file_path).st_size
            human_readable_size = humanize.naturalsize(size, gnu=True)
            result += "{size}    {file}\n".format(size=human_readable_size, file=file_path)
        return result