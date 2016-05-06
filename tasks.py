from multiprocessing import Pool
import subprocess

def do_compile(job):
    cmd = job.get_cmd()
    print(cmd)
    subprocess.call([job.compiler.path] + job.get_cmd_args().split(' '))

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
        self.pool.map(do_compile, self.jobs)

class StaticAnalysisTask(Task):
    pass

class DynamicAnalysisTask(Task):
    pass
