"""
If an action produces output file,
then that file is stored here.

If an action analyses one file,
then result of that analysis can be stored
as string in file.

Every result object can be retrieved from entity's
results dict by it's tag.

Result can be saved or loaded to disk.

Result can be further parsed by a ResultParser,
and stored in result model.
"""
from files import File
from os import path

class Result:
    extension = None
    tag = None
    analysis_output_file = None
    action_output_file = None

    def replaceExtension(self, extension):
        return self.name.replace('.c', extension)

    # def getAnalysisOutputPath(self):
    #     if tag:
    #         res_name = self.replaceExtension(self.extension)
    #         self.analysis_output = path.join(p, name)

    #     return self.analysis_output



class CompilationResult(Result):
    extension = ".out"
    tag = "compilation"

    def __init__(self, instance):
       self.instance = instance
       self.name = self.instance.parent.source.name

       self.action_output_file = self.get_action_output_file()

    def save(self):
        self.instance.results[self.tag] = self
        pass

    def load(self):
        if os.path.isfile(self.action_output_file.full_path):
            self.instance.results[self.tag] = self
            return True
        else:
            return False

    def get_action_output_file(self):
       p = self.instance.getOutputPath()
       act_name = self.replaceExtension( self.extension)

       return File(p, act_name)




