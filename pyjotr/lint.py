
import time
from pylint import reporters
import os


class LintCounters(object):

    def __init__(self):
        self.error = 0
        self.style = 0
        self.warning = 0
        self.runtime = 0

    def jsonify(self):
        return dict(
            error=self.error,
            style=self.style,
            warning=self.warning,
            runtime=self.runtime
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


class JsonLintReport(reporters.BaseReporter):

    def __init__(self):
        super(JsonLintReport, self).__init__()
        self.messages = {}
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
        if msg.msg_id[0] in ('C', 'R'):
            self.counters.style += 1
        elif msg.msg_id[0] in ('E', 'F'):
            self.counters.error += 1
        elif msg.msg_id[0] == 'W':
            self.counters.warning += 1

        l = self.messages[msg.path] if msg.path in self.messages else []
        if not l:
            self.messages[msg.path] = l

        l.append(JsonMessage(msg))

    def jsonify(self):
        return dict(
            counters=self.counters.jsonify(),
            errors={
                path: [msg.jsonify() for msg in msgs] for (path, msgs) in self.messages.items()
            }
        )
