
import unittest
from collections import namedtuple
import time
from io import StringIO
import sys
import traceback


(SUCCESS, FAILURE, ERROR, SKIPPED) = range(4)
ResultStatusMap = {
    SUCCESS: "success",
    FAILURE: "failure",
    ERROR: "error",
    SKIPPED: "skipped"
}

TestCounters = namedtuple("TestCounters",
                          ('successful', 'skipped', 'failed', 'runtime'))

class TestCounters(object):

    def __init__(self):
        self.successful = self.skipped = self.failed = self.runtime = 0

    def jsonify(self):
        return dict(
            successful=self.successful,
            skipped=self.skipped,
            failed=self.failed,
            runtime=self.runtime
        )


class TestInfo(object):

    def __init__(self, name, runtime=0, output="", message="", status=None):
        self.name = name
        self.runtime = runtime
        self.output = output
        self.message = message
        self.status = status

    def jsonify(self):
        return dict(
            status=ResultStatusMap[self.status],
            runtime=self.runtime,
            output=self.output,
            message=self.message,
            name=self.name
        )


class JsonTestResult(unittest.TestResult):

    def __init__(self):
        super(JsonTestResult, self).__init__()
        self.infos = []
        self.real_stdout = sys.stdout
        self.real_stderr = sys.stderr
        self.counters = TestCounters()

    def startTestRun(self, test):
        self.run_start_time = time.time()

    def stopTestRun(self, test):
        self.counters.runtime = int((time.time() - self.run_start_time)*1000.0)

    def startTest(self, test):
        self.start_time = time.time()
        self.active_info = TestInfo(
            name=type(test).__module__+'.'+type(test).__name__+'.'+test.id()
        )
        self.infos.append(self.active_info)
        sys.stdout = sys.stderr = StringIO()

    def stopTest(self, test):
        self.active_info.runtime = (time.time() - self.start_time)*1000.0
        self.active_info.output += sys.stdout.getvalue()
        sys.stdout = self.real_stdout
        sys.stderr = self.real_stderr
        if self.active_info.status == SUCCESS:
            self.counters.successful += 1
        elif self.active_info.status == SKIPPED:
            self.counters.skipped += 1
        else:
            self.counters.failed += 1    

    def addSuccess(self, test):
        self.active_info.status = SUCCESS

    def addFailure(self, test, err):
        self.active_info.status = FAILURE
        self.active_info.message = str(err[1])

    def addError(self, test, err):
        self.active_info.status = ERROR
        self.active_info.message = ''.join(
            traceback.format_exception(err[0], err[1], err[2])
        )

    def addSkip(self, test, reason):
        self.active_info.status = SKIPPED
        self.active_info.message = reason

    def addExpectedFailure(self, test, err):
        self.active_info.status = SUCCESS
        self.active_info.message = ''.join(
            traceback.format_exception(err[0], err[1], err[2])
        )

    def addUnexpectedSuccess(self, test):
        self.active_info = FAILURE
        self.active_info.message = "Test passed unexpectedly (was marked for failure)"

    def jsonify(self):
        return dict(
            counters=self.counters.jsonify(),
            results=[x.jsonify() for x in self.infos]
        )


class JsonTestRunner(object):
    def __init__(self):
        super(JsonTestRunner, self).__init__()

    def run(self, test):
        self.result = JsonTestResult()
        test(self.result)
        return self.result.counters.failed


