class PerfEstCSVPrinter:
    """
    This class has a result object as input.
    It will extract needed parsed data from the result object.
    After extraction, it will output perf est data in following format:

    function, block, norm_freq, i_count
    """
    result_tag = "perf_est_back"

    def __init__(self, instance_results):
        self.results = instance_results

    def get_report(self):
        output = ""

        perf_est_result = self.results[self.result_tag]
        perf_est_result.parse()

        data = perf_est_result.parsed_data['freq']

        for function in data.keys():
            for bb in data[function].keys():
                bb_data = data[function][bb]

                norm_freq = bb_data['norm_freq']
                i_count = bb_data['cnt']

                cols = [function, bb, norm_freq, i_count]

                output += ",".join(cols) + '\n'

        return output

