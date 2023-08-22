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


class TemplateFiltersMixin:

    @staticmethod
    def filter_localtime(timestamp):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

    @staticmethod
    def filter_format_bool(value, truevalue, falsevalue):
        return [falsevalue, truevalue][int(value)]

    @classmethod
    def set_filters(kls, env):
        for name in dir(kls):
            if name.startswith('filter_'):
                env.filters[name[7:]] = getattr(kls, name)


class ReportPlotsMixin:

    seq = args = result = scoreopts = iteropts = execopts = None
    checkpoints = None

    default_panel_height = [0, 400, 600, 700, 800] # by number of panels

    def plot_fitness_curve(self, skip_initial=True):
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0)
        view = slice(1, None) if skip_initial else slice(None)

        panel_fitness = go.Scatter(
            x=self.checkpoints.index[view], y=self.checkpoints['fitness'].iloc[view],
            mode='lines', name='Fitness')
        panel_mutation_rate = go.Scatter(
            x=self.checkpoints.index[view], y=self.checkpoints['mutation_rate'].iloc[view],
            mode='lines', name='Mutation rate')

        fig.add_trace(panel_fitness, row=1, col=1)

        for name, values in self.checkpoints.items():
            if not name.startswith('score:'):
                continue

            nvalues = values.iloc[view]
            nvalues -= nvalues.mean() # center the score (and don't scale)
            trace = go.Scatter(
                x=self.checkpoints.index[view], y=nvalues,
                mode='lines', name=name[6:])
            fig.add_trace(trace, row=2, col=1)

        fig.add_trace(panel_mutation_rate, row=3, col=1)

        fig.update_layout(
            title='Fitness changes over the iterations',
            height=self.default_panel_height[3])

        fig.update_yaxes(title_text='Total fitness', row=1, col=1)
        fig.update_yaxes(title_text='Fitness score (centered)', row=2, col=1)
        fig.update_yaxes(title_text='Mutation rate', row=3, col=1)
        fig.update_xaxes(title_text='Iteration', row=3, col=1)

        return pyo.plot(fig, output_type='div', include_plotlyjs=False)

    def plot_metric_curves(self, skip_initial=True):
        metrics = self.checkpoints.filter(regex='^metric:').columns

        fig = make_subplots(rows=len(metrics), cols=1, shared_xaxes=True, vertical_spacing=0.02)
        view = slice(1, None) if skip_initial else slice(None)

        for i, name in enumerate(metrics):
            nvalues = self.checkpoints[name].iloc[view]
            trace = go.Scatter(
                x=self.checkpoints.index[view], y=nvalues,
                mode='lines', name=name[7:])
            fig.add_trace(trace, row=i + 1, col=1)
            fig.update_yaxes(title_text=name[7:], row=i + 1, col=1)

        fig.update_layout(
            title='Individual metric change over the iterations',
            height=self.default_panel_height[-1])

        return pyo.plot(fig, output_type='div', include_plotlyjs=False)


class ReportGenerator(TemplateFiltersMixin, ReportPlotsMixin):

    def __init__(self, result, args, scoreopts, iteropts, execopts, seq,
                 scorefuncs):
        self.seq = seq
        self.args = args
        self.result = result
        self.scoreopts = scoreopts
        self.iteropts = iteropts
        self.execopts = execopts
        self.scorefuncs = scorefuncs

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
        scoreopts_filtered = {
            name: {k: v for k, v in opts.items() if not k.startswith('_')}
            for name, opts in self.scoreopts.items()
        }

        return {
            'args': self.args,
            'seq': self.seq,
            'scoring': scoreopts_filtered,
            'iter': self.iteropts,
            'exec': self.execopts,
            'params': self.parameters,
            'result': self.result,
            'checkpoints': self.checkpoints,
            'scorefuncs': self.scorefuncs,
            'plotters': {
                name[5:]: getattr(self, name)
                for name in dir(self)
                if name.startswith('plot_')
            },
        }

    def load_templates(self):
        template_loader = jinja2.PackageLoader('vaxpress', 'report_template')
        env = jinja2.Environment(loader=template_loader)
        self.set_filters(env)

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
    from vaxpress import scoring

    sfuncs = scoring.discover_scoring_functions([])

    ReportGenerator(runinfo['result'], runinfo['args'],
                    runinfo['scoring_options'], runinfo['iteration_options'],
                    runinfo['execution_options'], runinfo['seq'],
                    sfuncs).generate()