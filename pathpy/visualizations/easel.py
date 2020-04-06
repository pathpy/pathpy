#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : easel.py -- Environment to draw the pathpy objects
# Author    : Jürgen Hackl <hackl@ifi.uzh.ch>
# Time-stamp: <Mon 2020-04-06 12:13 juergen>
#
# Copyright (c) 2016-2019 Pathpy Developers
# =============================================================================

import os
import json
import subprocess
import errno
import webbrowser
import uuid

from string import Template

from .. import logger
from .tikz import TikzNetworkPainter
from .d3js import D3jsNetworkPainter

from http.server import SimpleHTTPRequestHandler, HTTPServer

import time
import threading


log = logger(__name__)


class Easel:
    def __init__(self, filename=None):
        if filename is None:
            self.filename = 'default'
        else:
            self.filename = filename


class PDF(Easel):
    def __init__(self, filename=None):

        # initialize base class
        super().__init__(filename=filename)

        # type of the container
        self.type = 'pdf'

        # easel of the pdf
        self.easel = None

        # final painting
        self.painting = None

    def draw(self, network, **kwargs):
        filename = os.path.splitext(os.path.basename(self.filename))[0]

        # create a tex document
        self.easel = TEX(filename+'.tex')

        # draw object
        self.easel.draw(network, **kwargs)

        # save object
        # easel.save()

        # get the painting
        self.painting = self.easel.painting

    def save(self, filename=None, **kwargs):

        config = self.painting.config

        clean = kwargs.get('clean', config['clean'])
        clean_tex = kwargs.get('clean_tex', config['clean_tex'])
        compiler = kwargs.get('compiler', config['compiler'])
        compiler_args = kwargs.get('compiler_args', config['compiler_args'])
        silent = kwargs.get('silent', config['silent'])

        if compiler_args is None:
            compiler_args = []

        # update the filename if given
        if filename is not None:
            self.filename = filename

        # get directories and file name
        current_dir = os.getcwd()
        output_dir = os.path.dirname(self.filename)

        # check if output dir exists if not use the base dir
        if not os.path.exists(output_dir):
            output_dir = current_dir
        basename = os.path.splitext(os.path.basename(self.filename))[0]

        # change to output dir
        os.chdir(output_dir)

        # save tex file
        self.easel.save(basename+'.tex')
        if compiler is not None:
            compilers = ((compiler, []),)
        else:
            latexmk_args = ['--pdf']

            compilers = (
                ('latexmk', latexmk_args),
                ('pdflatex', [])
            )

        main_arguments = ['--interaction=nonstopmode', basename + '.tex']

        for compiler, arguments in compilers:
            command = [compiler] + arguments + compiler_args + main_arguments

            try:
                output = subprocess.check_output(command,
                                                 stderr=subprocess.STDOUT)
            except Exception:
                # If compiler does not exist, try next in the list
                continue
            else:
                if not silent:
                    print(output.decode())

            if clean:
                try:
                    # Try latexmk cleaning first
                    subprocess.check_output(['latexmk', '-c', basename],
                                            stderr=subprocess.STDOUT)
                except (OSError, IOError, subprocess.CalledProcessError) as e:
                    # Otherwise just remove some file extensions.
                    extensions = ['aux', 'log', 'out', 'fls',
                                  'fdb_latexmk']

                    for ext in extensions:
                        try:
                            os.remove(basename + '.' + ext)
                        except (OSError, IOError) as e:
                            if e.errno != errno.ENOENT:
                                raise
            # remove the tex file
            if clean_tex:
                os.remove(basename + '.tex')
            # Compilation has finished,
            # so no further compilers have to be tried
            break

        # else:
        #     # Notify user that none of the compilers worked.
        #     log.error('No LaTex compiler was found! Either specify a LaTex '
        #               'compiler or make sure you have latexmk or pdfLaTex'
        #               ' installed.')
        #     raise AttributeError

        # change back to current dir
        os.chdir(current_dir)

        pass

    def show(self, **kwargs):

        # config = self.painting.config

        width = kwargs.get('width', 600)
        height = kwargs.get('height', 300)

        try:
            get_ipython
            from IPython.display import IFrame, display
            display(IFrame(self.filename, width=600, height=300))
        except:
            # get current directory
            current_dir = os.getcwd()

            # create temp file name
            filename = os.path.join(current_dir, self.filename)

            # open the file
            webbrowser.open(r'file:///'+filename)


class PNG(Easel):
    def __init__(self, filename=None):

        # initialize base class
        super().__init__(filename=filename)

        # type of the container
        self.type = 'png'

        # easel of the pdf
        self.easel = None

        # final painting
        self.painting = None

    def draw(self, network, **kwargs):
        filename = os.path.splitext(os.path.basename(self.filename))[0]

        # create a tex document
        self.easel = TEX(filename+'.tex')

        # draw object
        self.easel.draw(network, **kwargs)

        # save object
        # easel.save()

        # get the painting
        self.painting = self.easel.painting

    def save(self, filename=None, **kwargs):

        config = self.painting.config

        clean = kwargs.get('clean', config['clean'])
        clean_tex = kwargs.get('clean_tex', config['clean_tex'])
        compiler = kwargs.get('compiler', config['compiler'])
        compiler_args = kwargs.get('compiler_args', config['compiler_args'])
        silent = kwargs.get('silent', config['silent'])

        if compiler_args is None:
            compiler_args = []

        # update the filename if given
        if filename is not None:
            self.filename = filename

        # get directories and file name
        current_dir = os.getcwd()
        output_dir = os.path.dirname(self.filename)

        # check if output dir exists if not use the base dir
        if not os.path.exists(output_dir):
            output_dir = current_dir
        basename = os.path.splitext(os.path.basename(self.filename))[0]

        # change to output dir
        os.chdir(output_dir)

        # save tex file
        self.easel.save(basename+'.tex',
                        header_options='[convert={density=300,outext=.png}]')
        if compiler is not None:
            compilers = ((compiler, []),)
        else:
            latexmk_args = ['-shell-escape']

            compilers = (
                ('latexmk', latexmk_args),
                ('pdflatex', [])
            )

        main_arguments = ['--interaction=nonstopmode', basename + '.tex']

        for compiler, arguments in compilers:
            command = [compiler] + arguments + compiler_args + main_arguments

            try:
                output = subprocess.check_output(command,
                                                 stderr=subprocess.STDOUT)
            except Exception:
                # If compiler does not exist, try next in the list
                continue
            else:
                if not silent:
                    print(output.decode())

            if clean:
                try:
                    # Try latexmk cleaning first
                    subprocess.check_output(['latexmk', '-c', basename],
                                            stderr=subprocess.STDOUT)
                except (OSError, IOError, subprocess.CalledProcessError) as e:
                    # Otherwise just remove some file extensions.
                    extensions = ['aux', 'log', 'out', 'fls',
                                  'fdb_latexmk', 'ps', 'dvi']

                    for ext in extensions:
                        try:
                            os.remove(basename + '.' + ext)
                        except (OSError, IOError) as e:
                            if e.errno != errno.ENOENT:
                                raise
            # remove the tex file
            # if clean_tex:
            # Compilation has finished,
            # so no further compilers have to be tried
            break

        # else:
        #     # Notify user that none of the compilers worked.
        #     log.error('No LaTex compiler was found! Either specify a LaTex '
        #               'compiler or make sure you have latexmk or pdfLaTex'
        #               ' installed.')
        #     raise AttributeError

        # change back to current dir

        os.chdir(current_dir)

        pass

    def show(self, **kwargs):

        # config = self.painting.config

        width = kwargs.get('width', 600)
        height = kwargs.get('height', 300)

        try:
            get_ipython
            from IPython.display import IFrame, display
            display(IFrame(self.filename, width=600, height=300))
        except:
            # get current directory
            current_dir = os.getcwd()

            # create temp file name
            filename = os.path.join(current_dir, self.filename)

            # open the file
            webbrowser.open(r'file:///'+filename)


class TEX(Easel):
    def __init__(self, filename=None):

        # initialize base class
        super().__init__(filename=filename)

        # type of the container
        self.type = 'tex'

        # object to draw the plot
        self.painter = TikzNetworkPainter()

        # final painting
        self.painting = None

    def draw(self, network, **kwargs):

        # draw the network
        self.painting = self.painter.draw(network, **kwargs)

    def save(self, filename=None, **kwargs):

        # update the filename if given
        if filename is not None:
            self.filename = filename

        # get data and config from the painting
        data = self.painting.data
        config = self.painting.config

        standalone = config['standalone']

        header_options = kwargs.get('header_options', '')
        latex_header = '\\documentclass'+header_options+'{standalone}\n' + \
            '\\usepackage{tikz-network}\n' + \
            '\\begin{document}\n'
        latex_begin_tikz = '\\begin{tikzpicture}\n'
        latex_end_tikz = '\\end{tikzpicture}\n'
        latex_footer = '\\end{document}'
        latex_begin_scope = '\\begin{scope}'
        latex_end_scope = '\\end{scope}\n'

        w = config['width']
        h = config['height']

        latex_canvas = '\\clip (0,0) rectangle ({},{});\n'.format(w, h)

        with open(self.filename, 'w') as f:
            if standalone:
                f.write(latex_header)
            f.write(latex_begin_tikz)
            f.write(latex_canvas)

            for node in data['nodes']:
                f.write(node)
            for edge in data['edges']:
                f.write(edge)

            f.write(latex_end_tikz)
            if standalone:
                f.write(latex_footer)

    def show(self, **kwargs):
        pass


class CSV(Easel):
    def __init__(self, filename=None):

        # initialize base class
        super().__init__(filename=filename)

        # type of the container
        self.type = 'tex'

        # object to draw the plot
        self.painter = TikzNetworkPainter()

    def draw(self, network, **kwargs):
        self.painting = self.painter.draw(network, mode='csv', **kwargs)

    def save(self, filename=None, **kwargs):

        # update the filename if given
        if filename is not None:
            self.filename = filename

        # get data and config from the painting
        data = self.painting.data

        # if file name is a string get base name
        if isinstance(self.filename, str):
            filename = os.path.splitext(os.path.basename(self.filename))[0]
            filename_n = filename + '_nodes'
            filename_e = filename + '_edges'
        # if the file name is a tuple, use the first part for the node list and
        # the second part for the edge list.
        elif (isinstance(self.filename, tuple) or
              isinstance(self.filename, list)):
            filename_n = os.path.splitext(
                os.path.basename(self.filename[0]))[0]
            filename_e = os.path.splitext(
                os.path.basename(self.filename[1]))[0]
        else:
            log.error('File name is not correct specified!')
            raise AttributeError

        # write node list
        with open(filename_n+'.csv', 'w') as f:
            # f.write(self.drawers[0].node_drawer[0].head())
            for node in data['nodes']:
                f.write(node)

        # write edge list
        with open(filename_e+'.csv', 'w') as f:
            # f.write(self.drawers[0].edge_drawer[0].head())
            for edge in data['edges']:
                f.write(edge)

    def show(self, **kwargs):
        pass


class D3JS(Easel):

    def __init__(self, filename=None):
        # initialize base class
        super().__init__(filename=filename)

        # type of the container
        self.type = 'html'

        # base directory
        self.base_dir = str(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            os.path.normpath('visualizations/network')))

        # paninter who draws the plot
        self.painter = D3jsNetworkPainter()

        # final painting
        self.painting = None

    def draw(self, network, **kwargs):
        self.painting = self.painter.draw(network, **kwargs)

    def save(self, filename=None, **kwargs):

        from distutils.dir_util import copy_tree

        # update the filename if given
        if filename is not None:
            self.filename = filename

        # get directories and file name
        current_dir, output_dir = self._get_directories(self.filename)

        # get directories of d3js template
        d3js_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            os.path.normpath('visualizations/network'))

        # copy template to output directory
        copy_tree(d3js_dir, output_dir)

        data_file = os.path.join(
            output_dir,
            os.path.normpath('data/network.json'))

        config_file = os.path.join(output_dir, 'config.json')

        data = self.painting.data
        config = self.painting.config

        with open(data_file, 'w') as f:
            json.dump(data, f)

        with open(config_file, 'w') as f:
            json.dump(config, f)

    def _get_directories(self, filename):

        # get directories and file name
        current_dir = os.getcwd()
        file_dir = os.path.dirname(filename)

        # check if output dir exists if not use the base dir
        if not os.path.exists(file_dir):
            file_dir = current_dir
        basename = os.path.splitext(os.path.basename(filename))[0]

        output_dir = os.path.join(file_dir, basename)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        return current_dir, output_dir

    def show(self, **kwargs):
        data = self.painting.data
        config = self.painting.config

        port = kwargs.get('port', 8221)

        try:
            # check if python is used in a jupyter environment
            # TODO: find a more elegant method to do this.
            get_ipython

            from IPython.display import display_html

            # generate single html file
            html = self._generate_html(config, data, **kwargs)

            # display html file
            display_html(html, raw=True)

            # with open('thisisatest.html', 'w+') as f:
            #     f.write(html)

        except:

            log.debug('Not in an IPython environment.')

            # get current directory
            current_dir = os.getcwd()

            # create temp file name
            filename = os.path.join(current_dir, self.filename)

            # generate html file
            html = self._generate_html(config, data, **kwargs)

            # write file to disc
            # TODO: write temp file
            with open(filename, 'w+') as f:
                f.write(html)

            print(filename)
            # open the file
            webbrowser.open(r'file:///'+filename)

            # # get directories and file name
            # current_dir, output_dir = self._get_directories(self.filename)

            # # change to the output directory
            # os.chdir(output_dir)

            # # initialize server
            # server = PlotHTTPServer(('', port), SimpleHTTPRequestHandler)

            # # start server
            # thread = threading.Thread(target=server.run)
            # thread.start()

            # # open plot in browser
            # webbrowser.open("http://localhost:"+str(port))

            # try:
            #     while True:
            #         time.sleep(2)
            # except KeyboardInterrupt:
            #     log.debug('Stopping server ...')
            #     server.shutdown()
            #     log.debug('Server is stopped')
            #     thread.join()

            # # change back to the working directory
            # os.chdir(current_dir)

    def _generate_html(self, config, data, **kwargs):
        log.debug('Generate single html document.')
        widgets_id = 'x'+uuid.uuid4().hex
        network_id = 'x'+uuid.uuid4().hex

        # load template
        with open(os.path.join(self.base_dir, 'template.html')) as f:
            js_template = f.read()

        with open(os.path.join(self.base_dir, 'css/style.css')) as f:
            css_template = f.read()

        js = Template(js_template).substitute(divId=widgets_id,
                                              svgId=network_id,
                                              config=json.dumps(config),
                                              data=json.dumps(data))
        html = '<style>\n' + css_template + '\n</style>\n'
        html = html + \
            '<div id="{}"></div>\n<div id="{}"></div>\n'.format(
                widgets_id, network_id)
        html = html+js

        return html

    def _load_js_libraries(self):

        print(self.base_dir)
        # load required libraries
        from IPython.display import display, Javascript, HTML

        display(Javascript(
            "require.config({paths: {d3: 'https://d3js.org/d3.v5.min'}});"))
        display(Javascript(filename=self.base_dir+"/js/tooltip.js"))
        display(Javascript(filename=self.base_dir+"/js/network.js"))
        display(Javascript(filename=self.base_dir+"/js/widgets.js"))
        display(Javascript(filename=self.base_dir+"/js/slider.js"))
        display(HTML(filename=self.base_dir+"/css/style.css.html"))

    def _create_js_network(self, config, data):

        # load required libraries
        from IPython.display import display, Javascript, HTML

        # dump json to js
        display(Javascript("""
        (function(element){
            require(['d3','tooltip','network','widgets','slider'], function(d3,tooltip,network,widgets,slider){
            var config = %s
            var data = %s
            var myNetwork = network(config);
            widgets(element.get(0),config,myNetwork);
            if (config.temporal === true){
               slider(element.get(0),config,myNetwork);};
            myNetwork(element.get(0), data);
            });
        })(element);
        """ % (json.dumps(config),
               json.dumps(data))))


class PlotHTTPServer(HTTPServer):

    def __init__(self, server_address, handler):
        HTTPServer.__init__(self, server_address, handler)

    def run(self):
        try:
            self.serve_forever()
        except OSError:
            pass


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 79
# End:
