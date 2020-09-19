import datetime
import errno
import logging
import os
import shutil
import string
import unicodedata
import humanize

LOG = logging.getLogger(__name__)


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    cls.__str__ = __str__
    return cls


class DateUtils:
    WIN_EPOCH = datetime.datetime(1601, 1, 1)

    @classmethod
    def from_iso_format(cls):
        return datetime.date.fromisoformat

    @classmethod
    def now(cls):
        return datetime.datetime.now()

    @classmethod
    def now_formatted(cls, fmt):
        return DateUtils.now().strftime(fmt)

    @classmethod
    def add_microseconds_to_win_epoch(cls, microseconds):
        return DateUtils.WIN_EPOCH + datetime.timedelta(microseconds=microseconds)

    @classmethod
    def convert_to_datetime(cls, date_string, fmt):
        return datetime.datetime.strptime(date_string, fmt)

    @classmethod
    def convert_datetime_to_str(cls, datetime_obj, fmt):
        return datetime_obj.strftime(fmt)

    @classmethod
    def get_datetime(cls, y, m, d):
        return datetime.datetime(y, m, d)

    @classmethod
    def get_datetime_from_date(cls, date_obj, min_time=False, max_time=False):
        if not min_time and not max_time:
            raise ValueError("Either min_time or max_time had set to True!")

        if min_time:
            return datetime.datetime.combine(date_obj, datetime.datetime.min.time())
        if max_time:
            return datetime.datetime.combine(date_obj, datetime.datetime.max.time())


class StringUtils:
    @staticmethod
    def replace_special_chars(unistr):
        if not isinstance(unistr, str):
            LOG.warning("Object expected to be unicode: " + str(unistr))
            return str(unistr)
        normalized = unicodedata.normalize('NFD', unistr).encode('ascii', 'ignore')
        normalized = normalized.decode('utf-8')
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        valid_title = ''.join(c for c in normalized if c in valid_chars)
        return valid_title

    @staticmethod
    def convert_string_to_multiline(string, max_line_length, separator=" "):
        if not len(string) > max_line_length:
            return string

        result = ""
        curr_line_length = 0
        parts = string.split(separator)
        for idx, part in enumerate(parts):
            if curr_line_length + len(part) < max_line_length:
                result += part
                # Add length of part + 1 for space to current line length, if required
                curr_line_length += len(part)
            else:
                result += "\n"
                result += part
                curr_line_length = len(part)

            # If not last one, add separator
            if not idx == len(parts) - 1:
                result += separator
                curr_line_length += 1

        return result


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
    def ensure_file_exists_and_readable(cls, file, verbose=False):
        if verbose:
            LOG.info("Trying to open file %s for reading..", file)
        f = open(file, "r")
        if not f.readable():
            raise ValueError("File {} is not readable".format(file))
        return file

    @classmethod
    def ensure_file_exists_and_writable(cls, file, verbose=False):
        if verbose:
            LOG.info("Trying to open file %s for writing..", file)
        f = open(file, "w")
        if not f.writable():
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
    def copy_file_to_dir(src_file, dst_dir, dst_file_name_func, msg_template=None):
        dest_filename = dst_file_name_func(src_file, dst_dir)
        dest_file_path = os.path.join(dst_dir, dest_filename)

        if msg_template:
            LOG.info(msg_template.format(src_file, dest_file_path))
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

    @classmethod
    def get_file_extension(cls, filename):
        filename, ext = os.path.splitext(filename)
        ext = ext.replace(".", "")
        return ext

    @classmethod
    def write_to_file(cls, file_path, data):
        f = open(file_path, 'w')
        f.write(data)
        f.close()