from jobs import (
    CompilerOptions,
    FileExplorer,
    JobBuilder,
)

from settings import (
    SINGLE_SOURCE_TESTS_ROOT,
)

class Application:
    def __init__(self):
        self.options = CompilerOptions()

        self._explorer = FileExplorer(SINGLE_SOURCE_TESTS_ROOT)
        (self.source_list, self.include_dirs) = self._explorer.find()

        self._job_builder = JobBuilder(self.options, self.source_list)
        self.jobs = self._job_builder.build_jobs()

        for job in self.jobs:
            print(job)

    def run(self):
        print("running app!")
