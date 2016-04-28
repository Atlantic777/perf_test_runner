from multiprocessing import Pool

def do_compile(job):
    print("compiling: " + job.get_cmd())

class Task:
    workers = 1
    jobs = []
    pool = None

    def __init__(self, workers=1, jobs=[]):
        self.workers = workers
        self.jobs = jobs
        self.pool = Pool(processes=self.workers)

    def run(self):
        raise Exception("Not implemented!")

class CompilationTask(Task):
    def run(self):
        print("compiling...")
        self.pool.map(do_compile, self.jobs[:8])

class StaticAnalysisTask(Task):
    pass

class DynamicAnalysisTask(Task):
    pass
