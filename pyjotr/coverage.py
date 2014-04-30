
from coverage.report import Reporter
import os

class JsonFileCoverageCounters(object):

    def __init__(self):
        self.hits = 0
        self.misses = 0

    def jsonify(self):
        return dict(
            hits=self.hits,
            misses=self.misses
        )


class JsonFileCoverage(object):
    def __init__(self, path):
        self.path = path
        self.lines = {}
        self.counters = JsonFileCoverageCounters()

    def jsonify(self):
        return dict(
            path=self.path,
            lines=self.lines,
            counters=self.counters.jsonify()
        )


class JsonCoverageCounters(object):

    def __init__(self):
        self.files = 0
        self.hits = 0
        self.misses = 0

    def jsonify(self):
        return dict(
            files=self.files,
            hits=self.hits,
            misses=self.misses
        )

class JsonCoverageReport(Reporter):

    def __init__(self, cov, config):
        super(JsonCoverageReport, self).__init__(cov, config)
        #self.arcs = cov.data.has_arcs()
        #self.packages = {}
        self.path_strip_prefix = os.getcwd() + os.sep
        self.files = []
        self.counters = JsonCoverageCounters()

    def report(self, morfs=None, outfile=None):
        #self.packages = {}
        self.coverage._harvest_data()
        #self.coverage.config.from_args(
        #    ignore_errors=None, omit=None, include=None,
        #    show_missing=None
        #)
        self.report_files(self.json_file, morfs)
        self.counters.files = len(self.files)
        self.counters.misses = sum([f.counters.misses for f in self.files])
        self.counters.hits = sum([f.counters.hits for f in self.files])

    def json_file(self, cu, analysis):
        filename = cu.file_locator.relative_filename(cu.filename).replace('\\', '/')
        cfile = JsonFileCoverage(filename)
        for line in sorted(analysis.statements):
            cfile.lines[line] = int(line not in analysis.missing)

        cfile.counters.misses = len(analysis.missing)
        cfile.counters.hits = len(analysis.statements) - cfile.counters.misses
        self.files.append(cfile)

    def jsonify(self):
        return dict(
            counters=self.counters.jsonify(),
            files=[f.jsonify() for f in self.files]
        )
