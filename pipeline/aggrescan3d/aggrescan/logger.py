# -*- coding: utf-8 -*-

import os
import sys
from time import time, strftime, gmtime
import textwrap
import platform

_name = "Logger"

colors = {
    "blue": '\033[94m',
    "yellow": '\033[93m',
    'green': '\033[92m',
    'red': '\033[91m',
    'light_blue': '\033[96m',
    'purple': '\033[95m',
    'end': '\033[0m',
}

log_levels = {
    0: "[CRITICAL]",
    1: "[WARNING]",
    2: "[INFO]",
    3: "[OUT FILES]",
    4: "[DEBUG]"
}

color_prefix = {
    0: colors["red"] + "[CRITICAL]" + colors["end"],
    1: colors["yellow"] + "[WARNING]" + colors["end"],
    2: colors["blue"] + "[INFO]" + colors["end"],
    3: colors["purple"] + "[OUT FILES]" + colors["end"],
    4: colors["green"] + "[DEBUG]" + colors["end"],
}

_init_time = time()
_log_level = 2
_color = True
_stream = sys.stderr
_line_format = '%-20s %-19s%-75s %s\n'
_first_line_format = '%-20s %-19s%-75s \n'
_middle_line_format = '%-22s%-75s \n'
_last_line_format = '%-22s%-75s %s\n'
_line_break = 76
_remote = False
_prefix = color_prefix
_work_dir = ""


def setup(log_level=2, remote=False, work_dir=''):
    global _log_level, _color, _stream, _remote, _line_break, _prefix, _work_dir
    global _line_format, _middle_line_format, _first_line_format, _last_line_format
    _log_level = log_level
    _remote = remote
    _work_dir = work_dir
    if _remote or not sys.stderr.isatty():
        _color = False
        _line_format = '%-12s %-10s%-75s %s\n'
        _first_line_format = '%-12s %-10s%-75s \n'
        _middle_line_format = '%-22s %-75s \n'
        _last_line_format = '%-22s %-75s %s\n'
        _prefix = log_levels
    if _remote:
        _log_path = os.path.join(work_dir, "Aggrescan.log")
        try:
            _stream = open(_log_path, 'a+')
        except IOError:
            try:
                os.makedirs(work_dir)
                _stream = open(_log_path, 'a+')
            except OSError:
                warning(module_name=_name,
                        msg="Could not open a log file at %s. Writing to standard error instead." % _log_path)
            else:
                _stream.close()
                _stream = _log_path
        else:
            _stream.close()
            _stream = _log_path
    if platform.system() == "Windows":
        _color = False  # Windows doesn't support this way of coloring its logs in the command line
        _prefix = log_levels
    info(_name, 'Verbosity set to: ' + str(log_level) + " - " + log_levels[log_level])


def log_files():
    """
    :return: True if verbosity is high enough to save extra output (LOG FILE level)
    """
    return _log_level >= 3


def get_log_level():
    return _log_level


def coloring(color_name="light_blue", msg=""):
    if _color:
        return colors[color_name] + msg + colors["end"]
    return msg


def log(module_name="MISC", msg="Processing ", l_level=2, out=None):
    if out is None:
        # This is not great but should use stderr if there's a problem with log file, hopefully no race happens
        # This whole thing is attempting to force the log to really flush its data in real time
        try:
            out = open(_stream, 'a+')
        except TypeError:       # This should mean _stream is actually stderr
            out = _stream
    if l_level <= _log_level:
        t = gmtime(time() - _init_time)
        if len(msg) < _line_break:
            msg = _line_format % (
                _prefix[l_level], coloring(msg=module_name + ":", color_name='light_blue'),
                msg, strftime('(%H:%M:%S)', t)
            )
            out.write(msg)
            out.flush()
        else:
            lines = textwrap.wrap(msg, width=_line_break-1)
            first_line = _first_line_format % (
                _prefix[l_level], coloring(msg=module_name + ":", color_name='light_blue'), lines[0]
            )
            out.write(first_line)
            for lineNumber in xrange(1, len(lines) - 1):
                line = _middle_line_format % (" ", lines[lineNumber])
                out.write(line)
            final_line = _last_line_format % (" ", lines[-1], strftime('(%H:%M:%S)', t))
            out.write(final_line)
            out.flush()

        if out is not sys.stderr:
            out.close()


def critical(module_name="_name", msg=""):
    log(module_name=module_name, msg=msg, l_level=0)


def warning(module_name="_name", msg=""):
    log(module_name=module_name, msg=msg, l_level=1)


def info(module_name="_name", msg=""):
    log(module_name=module_name, msg=msg, l_level=2)


def log_file(module_name="_name", msg=""):
    log(module_name=module_name, msg=msg, l_level=3)


def debug(module_name="_name", msg=""):
    log(module_name=module_name, msg=msg, l_level=4)


def to_file(filename='', content='', msg='', allow_err=True, traceback=True):
    """

    :param filename: path for the file to be saved
    :param content: a string to be saved (be careful not to pass a string that is too long
    :param msg: optional: a message to be logged
    :param allow_err: if True a warning will be logged on OSError, if False program exit call will be made
    :param traceback: if True an Exception will be raised on exit call
    :return:
    """
    if filename and content:
        try:
            if os.path.isfile(filename):
                log_file(module_name=_name, msg="Overwriting %s" % filename)
            with open(filename, 'w') as f:
                f.write(content)
        except IOError:
            if allow_err:
                warning(module_name=_name, msg="IOError while writing to: %s" % filename)
            else:
                exit_program(module_name=_name, msg="IOError while writing to: %s" % filename, traceback=traceback)
    if msg:
        log_file(module_name=_name, msg=msg)


def exit_program(module_name=_name, msg="Shutting down", traceback=None, exc=None):
    """
    Exits the program, depending on options might do it quietly, raise, or print traceback
    :param module_name: string with  the calling module's name
    :param msg: string, message to be printed when the program exits
    :param traceback: str, if log level is high traceback will be printed
    :param exc: a specific exception passed by the caller
    :return: None
    """

    if exc:
        _msg = '%s: %s' % (msg, exc.message)
    else:
        _msg = msg
    critical(module_name=module_name, msg=_msg)
    if _log_level > 3 and traceback:
        _stream.write(traceback)
    sys.exit(1)


def record_exception(trace_stack):
    global _work_dir
    with open(os.path.join(_work_dir, "Aggrescan.error"), 'w') as f:
        file_header = "Aggrescan encountered an error and it wasn't one we were expecting. \n" \
                      "Please see the the following Traceback, perhaps it will be helpfull in understanding what happened.\n" \
                      "We would be grateful if you reported the incident to one of the authors so we can correct the error.\n"
        f.write(file_header)
        f.write(trace_stack)


class AggrescanError(Exception):
    """Generic class for Aggrescan Exceptions that should be handled or otherwise logged
        The subclasses are meant to do most of the work, so this is obviously work in progress
        and hopefully subclasses will do more in the future"""
    def __init__(self, *args, **kwargs):
        self.module_name = ""
        self.log_if_remote = ""
        self.work_dir_error = ""
        self.error_msg = ""
        self.err_file = ""
        if "module_name" in kwargs:
            self.module_name = kwargs["module_name"]
        if "err_file" in kwargs:    # Prevents the error log from being created - since the error is path/dir related
            self.err_file = kwargs["err_file"]
        if "work_dir_error" in kwargs:
            self.work_dir_error = True
        self.logger_msg = self.module_name + " encountered an error"
        if args:
            self.error_msg = args[0]
        Exception.__init__(self, *args)
    # This function and err_file serve a somewhat convoluted function - they split what is the message
    # to be displayed on screen and the one that would be logged in a file into two separate places using a proxy -
    # extra error file

    def generate_error_file(self):
        global _work_dir
        if not self.work_dir_error:
            out_file = os.path.join(_work_dir, "Aggrescan.error")
            file_header = "One of Aggrescan3D modules (%s) encountered an error. \n" % self.module_name
            with open(out_file, 'a+') as f:
                if self.err_file:
                    f.write(file_header)
                    with open(os.path.join(_work_dir, self.err_file), 'r') as err_file:
                        f.write(err_file.read())
                else:
                    f.write(file_header)
                    f.write(self.error_msg)


class FoldXError(AggrescanError):
    def __init__(self, *args, **kwargs):
        _module_name = "FoldX"
        AggrescanError.__init__(self, *args, module_name=_module_name, **kwargs)


class CabsError(AggrescanError):
    def __init__(self, *args, **kwargs):
        _module_name = "CABS"
        AggrescanError.__init__(self, *args, module_name=_module_name, **kwargs)


class ASAError(AggrescanError):
    def __init__(self, program_name, filename):
        _module_name = "ASA"
        msg = "Aggrescan encountered an error while performing accessibility calculations with %s. " \
              "See the details in the Aggrescan.error file in your working directory." % program_name
        AggrescanError.__init__(self, msg, module_name=_module_name, err_file=filename)


class InputError(AggrescanError):
    def __init__(self, *args):
        _module_name = "OptParser"
        AggrescanError.__init__(self, *args, module_name=_module_name)
