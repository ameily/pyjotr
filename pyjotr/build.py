
import time
from pyjotr import lint, tests
from pyjotr.coverage import JsonCoverageReport


class JsonBuild(object):

    def __init__(self, id=None, server=None, commit=None, branch=None,
                 runner=None, author=None,  message=None, timestamp=None,
                 trace=None, coverage=None):
        self.id = id
        self.server = server
        self.commit = commit
        self.branch = branch
        self.runner = runner
        self.author = author
        self.message = message
        self.timestamp = timestamp or int(time.time()*1000.0)
        self.trace = trace
        self.runtime = 0
        self.status = None

        if not self.runner:
            import socket
            self.runner = socket.gethostname()

        self.lint_report = lint.JsonLintReport()
        self.test_runner = tests.JsonTestRunner()
        self.coverage_report = None
        if coverage:
            self.coverage_report = JsonCoverageReport(coverage, coverage.config)

    def parse_git(self):
        import subprocess
        proc = subprocess.Popen(['git', 'log', '-1', '--pretty=%an <%ae>\n%B'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        raw = proc.stdout.read().decode()
        lines = raw.split('\n')

        self.author = lines[0].strip() if lines else ''
        self.message = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''

    def finalize(self):
        if self.coverage_report:
            self.coverage_report.report()

        self.runtime = int((time.time()*1000.0) - self.timestamp)
        self.test_result = self.test_runner.result
        if self.test_result.counters.failed:
            self.status = -1
        else:
            self.status = 0

    def jsonify(self):
        return dict(
            build=dict(
                runtime=self.runtime,
                id=self.id,
                server=self.server,
                runner=self.runner,
                commit=self.commit,
                branch=self.branch,
                message=self.message,
                author=self.author,
                timestamp=self.timestamp,
                status=self.status,
                trace=self.trace
            ),
            tests=self.test_result.jsonify(),
            lint=self.lint_report.jsonify(),
            coverage=self.coverage_report.jsonify()
        )
