#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,shutil
import logger
from newRunJob import Job
import optparser as opt
import traceback as _tr

_name = "Main"


def _cleanup(aggrescan_job_instance):
    """
    Done to prevent a situation where Job raises an error on initialization and there is nothing to delete
    Normally deletes or keeps the simulations temporary directory depending on verbosity settings
    (Can't check for Exceptions in finally block, hence the function)
    """
    try:
        if logger.get_log_level() < 4:
            shutil.rmtree(aggrescan_job_instance.get_tempdir(),ignore_errors=True)
            logger.log_file(module_name=_name, msg="Removing temporary files")
        else:
            logger.log_file(module_name=_name,
                            msg="Verbosity higher than 3 - temporary files kept in %s"
                                % aggrescan_job_instance.get_tempdir())
    except AttributeError:
        pass


def run_program():
    try:
        a = "dummy"  # to avoid cleanup on empty instances
        options = opt.parse(options=sys.argv[1:])
        logger.setup(log_level=options['verbose'], remote=options['remote'], work_dir=options["work_dir"])
        a = Job(config=options)
        a.run_job()
        _cleanup(a)
        logger.info(module_name="Main", msg="Simulation completed successfully.")

    except KeyboardInterrupt:
        _cleanup(a)
        logger.info(module_name=_name, msg="Interrupted by user")

    except logger.AggrescanError as custom_error:
        _cleanup(a)
        custom_error.generate_error_file()
        logger.exit_program(module_name=custom_error.module_name,
                            msg=custom_error.logger_msg,
                            traceback=None,
                            exc=custom_error)

    except Exception as e:
        _cleanup(a)
        logger.record_exception(trace_stack=_tr.format_exc())
        logger.critical(module_name=_name,
                        msg="Unhandled Exception caught: %s." % e.message)
        if logger.get_log_level() > 2:
            logger.info(module_name=_name,
                        msg="Verbosity higher than 2 - raising the Exception to provide traceback.")
            raise
        else:
            logger.exit_program()
