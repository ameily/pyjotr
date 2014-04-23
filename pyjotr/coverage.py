
from coverage.report import Reporter
import os

class JsonCoverageReport(Reporter):

    def __init__(self, cov, config):
        super(JsonCoverageReport, self).__init__(cov, config)
        self.arcs = cov.data.has_arcs()
        self.packages = {}
        self.path_strip_prefix = os.getcwd() + os.sep

    def report(self, morfs=None, outfile=None):
        self.packages = {}
        self.coverage._harvest_data()
        self.coverage.config.from_args(
            ignore_errors=None, omit=None, include=None,
            show_missing=None
        )
        self.report_files(self.json_file, morfs)

    def json_file(self, cu, analysis):
        #print("json_file(", repr(cu), ",", type(analysis))
        filename = cu.file_locator.relative_filename(cu.filename)
        print(filename)

