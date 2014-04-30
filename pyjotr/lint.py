
import time
from pylint import reporters
import os


class LintCounters(object):

    def __init__(self):
        self.errors = 0
        self.advice = 0
        self.warnings = 0
        self.runtime = 0
        self.files = 0

    def jsonify(self):
        return dict(
            errors=self.errors,
            advice=self.advice,
            warnings=self.warnings,
            runtime=self.runtime,
            files=self.files
        )


class JsonMessage(object):

    def __init__(self, msg):
        self.line = msg.line
        self.code = msg.msg_id
        self.symbol = msg.symbol
        self.obj = msg.obj
        self.column = msg.column
        self.msg = msg.msg

    def jsonify(self):
        return dict(
            line=self.line,
            code=self.code,
            symbol=self.symbol,
            obj=self.obj,
            column=self.column,
            msg=self.msg
        )


class JsonLintFileCounters(object):

    def __init__(self):
        self.errors = self.advice = self.warnings = 0

    def jsonify(self):
        return dict(
            errors=self.errors,
            advice=self.advice,
            warnings=self.warnings
        )


class JsonLintFile(object):

    def __init__(self, path):
        self.path = path
        self.counters = JsonLintFileCounters()
        self.advice = []
        self.errors = []
        self.warnings = []

    def jsonify(self):
        return dict(
            path=self.path,
            counters=self.counters.jsonify(),
            advice=[msg.jsonify() for msg in self.advice],
            errors=[msg.jsonify() for msg in self.errors],
            warnings=[msg.jsonify() for msg in self.warnings]
        )


class JsonLintReport(reporters.BaseReporter):

    def __init__(self):
        super(JsonLintReport, self).__init__()
        self.files = {}
        self.path_strip_prefix = os.getcwd() + os.sep
        self.counters = LintCounters()
        self.start_time = None

    def _display(self, layout):
        pass

    def on_set_current_module(self, module, filepath):
        if not self.start_time:
            self.start_time = time.time()

    def on_close(self, stats, previous_stats):
        self.counters.runtime = int((time.time() - self.start_time)*1000.0)

    def add_message(self, msg_id, location, msg):
        msg = reporters.Message(self, msg_id, location, msg)
        msg.path = msg.path.replace('\\', '/')

        lfile = None
        if msg.path in self.files:
            lfile = self.files[msg.path]
        else:
            lfile = JsonLintFile(msg.path)
            self.files[msg.path] = lfile
            self.counters.files += 1

        if msg.msg_id[0] in ('C', 'R'):
            self.counters.advice += 1
            lfile.counters.advice += 1
            lfile.advice.append(JsonMessage(msg))
        elif msg.msg_id[0] in ('E', 'F'):
            self.counters.errors += 1
            lfile.counters.errors += 1
            lfile.errors.append(JsonMessage(msg))
        elif msg.msg_id[0] == 'W':
            self.counters.warnings += 1
            lfile.counters.warnings += 1
            lfile.warnings.append(JsonMessage(msg))

    def jsonify(self):
        return dict(
            counters=self.counters.jsonify(),
            files=[
                self.files[path].jsonify() for path in self.files
            ]
        )
