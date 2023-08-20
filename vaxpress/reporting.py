#
# VaxPress
#
# Copyright 2023 Hyeshik Chang
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# “Software”), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import plotly.offline as pyo
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import jinja2
import os
import json
import time

template_dir = os.path.join(os.path.dirname(__file__), 'report_template')

def filter_timestamp_local(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


class ReportPlotsMixin:

    seq = args = result = scoreopts = iteropts = execopts = None
    checkpoints = None

    default_panel_height = [0, 400, 600] # by number of panels

    def plot_fitness_curve(self):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)

        panel_fitness = go.Scatter(
            x=self.checkpoints.index, y=self.checkpoints['fitness'],
            mode='lines', name='Fitness')
        panel_mutation_rate = go.Scatter(
            x=self.checkpoints.index, y=self.checkpoints['mutation_rate'],
            mode='lines', name='Mutation rate')

        fig.add_trace(panel_fitness, row=1, col=1)
        fig.add_trace(panel_mutation_rate, row=2, col=1)

        fig.update_layout(
            title='Fitness changes over the iterations',
            height=self.default_panel_height[2])

        fig.update_yaxes(title_text="Fitness score", row=1, col=1)
        fig.update_yaxes(title_text="Mutation rate", row=2, col=1)
        fig.update_xaxes(title_text="Iteration", row=2, col=1)

        return pyo.plot(fig, output_type='div', include_plotlyjs=False)


class ReportGenerator(ReportPlotsMixin):

    def __init__(self, result, args, scoreopts, iteropts, execopts, seq):
        self.seq = seq
        self.args = args
        self.result = result
        self.scoreopts = scoreopts
        self.iteropts = iteropts
        self.execopts = execopts

        self.templates = self.load_templates()

    def generate(self):
        params = self.prepare_data()

        for name, template in self.templates.items():
            if name.endswith('.html'):
                output = template.render(**params)
                open(os.path.join(self.execopts.output, name), 'w').write(output)

    def prepare_data(self):
        self.parameters = json.load(open(self.execopts.output + '/parameters.json'))
        self.checkpoints = pd.read_csv(self.execopts.output + '/checkpoints.tsv',
                                       sep='\t', index_col=0)

        return {
            'args': self.args,
            'seq': self.seq,
            'scoring': self.scoreopts,
            'iter': self.iteropts,
            'exec': self.scoreopts,
            'params': self.parameters,
            'result': self.result,
            'checkpoints': self.checkpoints,
            'plotters': {
                name[5:]: getattr(self, name)
                for name in dir(self)
                if name.startswith('plot_')
            },
        }

    def load_templates(self):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        env.filters['localtime'] = filter_timestamp_local

        return {
            name: env.get_template(name)
            for name in env.list_templates()
        }


if __name__ == '__main__':
    import sys
    sys.path.append('.')

    rundir = 'testrun-dev'
    import pickle
    runinfo = pickle.load(open(rundir + '/report_data.pickle', 'rb'))

    ReportGenerator(runinfo['result'], runinfo['args'],
                    runinfo['scoring_options'], runinfo['iteration_options'],
                    runinfo['execution_options'], runinfo['seq']).generate()