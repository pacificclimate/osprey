import io
import pytest
from contextlib import redirect_stderr, redirect_stdout
from wps_tools.testing import run_wps_process
import sys


def process_err_test(process, datainputs):
    err = io.StringIO()
    with redirect_stderr(err), pytest.raises(Exception):
        run_wps_process(process(), datainputs)

    assert "pywps.app.exceptions.ProcessError" in err.getvalue()
    err.close()
