class Executor:
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager


    def execute(self, JobClass, scope, force=False, verbose=False):
        self.JobClass = JobClass
        self.scope = scope
        self.force = force
        self.verbose = verbose

        self.triggerIt()

    def get_instance_list(self):
        if self.scope.domain == 'everything':
            for instance in self.entity_manager.all_instances():
                if self.check_instance(instance):
                    yield instance
        elif self.scope.domain == 'entity' and self.scope.entity is not None:
            entity = self.entity_manager.get_entity(self.scope.entity)
            print(entity)
            for instance in entity.all_instances():
                if self.check_instance(instance):
                    yield instance


    def check_instance(self, instance):
        if (instance.compiler.name in self.scope.compilers) and \
        (instance.opt in self.scope.opts):
            return True
        else:
            return False

    def triggerIt(self):
        for instance in self.get_instance_list():
            self.run(instance)


    def run(self, instance):
        if self.verbose:
            print("Executing action on: " + str(instance))

        includes = self.entity_manager.include_dirs
        self.job = self.JobClass(instance, includes)
        self.job.run(force=self.force, verbose=self.verbose)
