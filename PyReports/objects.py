#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 17:33:20 2022

@author: Sina Tureli

Non-container objects used in the module. _Context and _Node are two internal
classes from which all other objects (including container objects in the con
containers module) derive from. All other objects are meant to be employed
by the end user.

"""

import matplotlib as _mpl
import base64 as _b64
import random as _rand
import string as _str
import re as _re
import plotly as _plotly
import PIL as _PIL
import os as _os
import ntpath as _ntp

import PyReports as pr
from . import _internal
from pathlib import PosixPath

_NoneType = type(None)
cdir = _os.path.dirname(__file__)
css_dir = _os.path.join(cdir,'css')

class _Context():
    """
    For adding context manager functionality to reports and section which facilitates
    easy report writing. The code is similiar to the one in

    https://docs.pymc.io/en/v3/

    however creation of the context as a thread local variable seems unnecessary
    for purposes of report generation so that is removed.
    """

    _contexts = {'stack':[]}
    _loading_from_json = False

    def __init__(self):
        pass


    def __enter__(self):
        type(self)._get_contexts().append(self)

        return self


    def __exit__(self, typ, value, traceback):
        type(self)._get_contexts().pop()


    @classmethod
    def _get_contexts(cls):

        return cls._contexts['stack']


    @classmethod
    def _get_context(cls):
        """Return the deepest context on the stack."""
        try:
            return cls._get_contexts()[-1]
        except IndexError:
            raise TypeError("No context on context stack")



class _Node():
    '''
    A report is given the structure of a tree where containers and objects
    are nodes. The graph structure infers two advantages, it makes formatting
    the html code much easier so it is easy to read. It also has the advantage
    of being able to use recursion for a variety of tasks such as rendering the
    report as html or as json.

    Not using a ready made python module like anytree because I only need very
    simple propoerties of a tree and not all the other stuff so no need to bloat
    this package

     _Node object is not meant to be used by the public user. When a non-report
     object such as a section is created, it is either done through the
     functionality provided by its parent such as

     report = Report('report title')
     section = report.section('section title')
     section.txt('Some text in section1')

     or equilvalently:

     report = Report('report title')
     section = Section('section title', parent=report)
     Text('Some text in section1', parent=section)

     However the recommended method is via the context method:

     with Report('report title') as report:

         with Section('section title'):

             Text('Some text in section1')

    The two methods generate exactly the same report with the latter one
    having the advantage that you will not need to retype section multiple
    times if you are writing a length report. It also makes it much easier
    to visually gauge the structure of the report simply from the code and
    makes modifications to the report much easier.

    In the latter method, the Section and Text class initializations infer their
    parents from context (achieved through the _Context class).

    '''

    def __init__(self, parent=None):


        if parent is None:                                                 # if parent is None see if it has been created
                                                                           # to the last element of the context stack
            try:
                parent = _Context._get_context()
            except TypeError:
                if not isinstance(self, (pr.containers.Report, pr.containers.Section)):
                    raise TypeError('Non Report or Non Section nodes can only '
                                     'be created with a parent input or with a '
                                     'context (using with). A node of type '
                                     f'{type(self)} was created with a parent of '
                                     f'type {type(parent)}.'
                                     )

        else:
            assert isinstance(parent, _Node), f'parent should be a _Node but is {type(parent)}'

        self._parent = parent
        self._children = []


    def remove(self, node):
        '''
        Facilitates removal of children from Node while sorting out parent
        child relations.

        For instance to remove a section1 that is directly a child of a report1
        than say report1.remove(section1). If you want to remove a subsection1
        which is a part of section1 then you can say section1.remove(subsection1)
        which will remove subsection1 and any of its subcontents. You can also
        say report.remove(subsection1) which will recursively search for this
        subsection and remove it too.
        '''

        if isinstance(node,_Node) and node in self._children:
            node.__dict__['_parent'] = None
            self._children.remove(node)

        node_ind = 0
        while not node._is_root and node_ind<len(self._children):
            self._children[node_ind].remove(node)
            node_ind += 1


    def to_json(self,  path):

        '''
        This function saves a _Node's info as json. It is just a convenience
        extension to the _Node class and directly calls the to_json function
        from io.py

        Main usage is to save reports as json so that they can be loaded else
        where and modified via PyReports package without having to modify the
        original code that created the report.

        The json created as such can be loaded via the from_json function below.
        '''

        pr._io.to_json(self, path)



    def summary(self, _depth=None, _print_root=None, debug = False, detailed=False,
                formatting='none', link_to_sections=False):
        '''
        A less detailed version of __str__, only sections are printed

        If debug = True, object addresses are printed instead of titles
        and non section objects are printed too.

        Formatting can be none, terminal, html or markdown so that if you want
        to paste/display the tree somewhere, you can change the formatting.

        '''
        return pr._io.to_ascii(self, detailed=detailed, print_address=debug,
                        _depth=None, _print_root=self, formatting=formatting,
                        link_to_sections=link_to_sections)


    @property
    def _is_root(self):

        return self._parent is None


    def _ancestors(self, until=None):

        ancestors = [self]

        if self._parent is None or self==until:
            return ancestors
        else:
            ancestors = self._parent._ancestors(until) + ancestors

        return ancestors


    def _descendants(self, section_only=False):

        descendants = [self]
        iter_over = []

        if section_only and hasattr(self,'sections'):
            iter_over = self.sections

        if not section_only:
            iter_over = self._children

        if len(iter_over)==0:
            return descendants

        for item in iter_over:
            descendants += item._descendants(section_only=section_only)

        return descendants


    def _add_child(self, child):

        assert isinstance(child, _Node), f'Child should be a Node object but was {type(child)}'

        self._children.append(child)


    def _remove_child(self, child):

        self._children.remove(child)
        child._set_parent(None)


    def _set_parent(self, parent):

        self.__dict__['_parent'] = parent
        if parent is not None and self not in parent._children:
            parent._add_child(self)


    def _root(self, until=None):

        if self._is_root:
            return self
        else:
            parent = self._parent

            while not parent._is_root and parent != until:
                parent = parent._parent

            return parent


    @property
    def _depth(self):

        '''
        Return the depth of a node in the graph that represents the report.
        It is better to call this function when needed rather then store
        this as a variable when the Node is created because this value
        might change if someone creative enough messes with the child and
        parent relations
        '''

        if self._is_root:
            return 0
        else:
            depth = 1
            parent = self._parent

            while not parent._is_root:
                depth += 1
                parent = parent._parent

            return depth


    def _check_types(self, arg_names, args, expected_types, fun_name):
        '''
        This is a function used to check function input types for methods of _Node derived
        classes. Implemented only for functions which are expected to be called
        by the user and not internal functions.
        '''

        if not isinstance(arg_names,list):arg_names = [arg_names]
        if not isinstance(args,list):args = [args]
        if not isinstance(expected_types,list):expected_types = [expected_types]

        class_name = _re.search(r'\.[^\.\']+\'',str(type(self))).group()[1:-1]

        for arg_name, arg, expected_type in zip(arg_names, args, expected_types):
            if not isinstance(arg, expected_type):

                arg_type = type(arg)

                raise ValueError(f'{arg_name} input to {class_name}.{fun_name} '
                                 f'is expected to be {expected_type} but is '
                                 f'{arg_type}')


    def _parent_child_relation_checker(self, parent):

        '''
        hallmark of fascism, preventing creative use of parent child relations
        '''

        if parent is not None and not isinstance(parent, _Node):
            raise ValueError(f'parent should be None or _Node but is {type(parent)}')

        if type(parent) in dir(pr.objects):
            raise ValueError('classes from objects module can not be a parent '
                             f'(in this case a {type(parent)} was set as parent).')

        if isinstance(self,pr.containers.Report) and parent is not None:
            raise ValueError(f'Parent of a Report can only be None but was {type(parent)}.')

        if (isinstance(self,pr.containers.Section) and not parent is not None and
            isinstance(parent,(pr.containers.Report,pr.containers.Section))):
            raise ValueError('Parent of a Section can only be a Report, Section '
                             f' or None but it was {type(parent)}.')

        if type(self) in dir(pr.objects) and isinstance(type(parent), pr.containers.Report):
            raise ValueError('classes from objects can not be children of a Report.')


    def __setattr__(self, key, value):

        '''
        By modifying setattr we provide a convenient way to remove nodes
        or branches from the graph

        By just saying object._parent = new_parent_object, you sort out the parent child
        relations in one go without having to worry about if you make the correct
        changes to both the parent and the child in terms of inheritance.

        There is some fascistic type checking to make sure one can not do weird
        stuff like try to set the parent of a Report as an image etc.
        '''

       	if key == '_parent':

            self._parent_child_relation_checker(value)

            if hasattr(self, '_parent') and self._parent is not None:
                self._parent._remove_child(self)

            if value is not None:
                value._add_child(self)

       	self.__dict__[key] = value


    def __str__(self, _depth=None, _print_root=None):

        '''
        A more detailed version of summary, non-sections objects are also printed

        As the correct formatting of the ascii graph is quite tedious, it was
        a design choice to neatly tuck it away in io rather than bloat this
        simple class
        '''

        return pr._io.to_ascii(self, detailed=True, print_address=False,
                        _depth=None, _print_root=self)



class Link(_Node):

    """
    Link object: It is a link.
    """

    def __init__(self, link, link_title=None, parent=None, link_style = None,
                 end='<br><br>'):

        pr.objects._Node.__init__(self, parent)

        if link_title is None:
            link_title = _ntp.basename(link)

        link = str(link)

        assert isinstance(link_title,str),f'link title should be a string but is {type(link_title)}'
        assert isinstance(end,str),f'end should be a string but is {type(end)}'

        if link_style is None:
            link_style = ''

        assert isinstance(link_style,str), f'link_style should be a string but is {type(link_style)}'

        self._link = link
        self._link_title = link_title
        self._link_style = link_style
        self._end = end


    def _generate_html(self):

        parent_depth = self._parent._depth

        return '\n' + '    '*(parent_depth + 1) + f'<a href="{self._link}" style="{self._link_style}">{self._link_title}</a>\n' + self._end


class Code(_Node):

    """
    Code object: Prints a code on the html page with syntax highlighting
    using code-prettify.js https://github.com/googlearchive/code-prettify
    """

    def __init__(self, code_text:str, parent:_Node=None, linenums:int=None,
                  end:str= ' ', fold_code=True):

        if fold_code and not _Context._loading_from_json:
            fold = pr.containers.Fold()
            pr.objects._Node.__init__(self, fold)
        else:
            pr.objects._Node.__init__(self, parent)

        self._check_types(['code_text', 'parent', 'linenums', 'end','fold_code'],
                          [code_text, parent, linenums, end, fold_code],
                          [str, (_Node,_NoneType), (int,_NoneType), str, bool],
                          '__init__')

        self._code_text = code_text
        self._linenums = linenums
        self._end = end
        self._fold_code = fold_code


    def _format_code_text(self, text):

        code_text = _internal.format_text(text, parent_depth=0,
                                          leading_space=' ', is_code=True)

        code_text = code_text.replace('<br>','')

        return code_text


    def _generate_html(self):

        tag = ('\n<pre class="prettyprint"' +
               'linenums:{self._linenums}"'*(self._linenums is not None) +
               '>'
               )

        formatted_code_text = self._format_code_text(self._code_text)

        html_str =  f'{tag}\n'
        html_str += '\n' + f'{formatted_code_text}\n'
        html_str += '</pre>\n'

        return html_str


class Text(_Node):

    """
    Text object: Can define font size and alignment of text with inputs.
    Note meant to be initialized from scratch but called from a Section
    object as it needs a parent
    """

    def __init__(self, text, parent=None, font_size=16, alignment='left', end='',
                 style='', formatted=False):


        pr.objects._Node.__init__(self, parent)

        assert alignment in ['left','right','center'], 'alignment should be left right or center'
        assert isinstance(text,str),'Text should be a str'
        assert isinstance(font_size, (float,int)), 'Font size should be numeric'
        assert font_size>0, 'Font size should be larger than 0'


        self._text = text
        self._font_size = font_size
        self._alignment = alignment
        self._end = end
        self._style = style
        self._formatted = formatted

    def _format_text(self, text):

        parent_depth = self._parent._depth

        text = _internal.format_text(text, parent_depth, formatted=self._formatted)

        return text


    def _generate_html(self):

        parent_depth = self._parent._depth
        text = self._text
        style = self._style

        tags = [f'<p style = "font-size:{str(self._font_size)}px; text-align:{self._alignment}; {style}">','</p>']
        endline = '\n'

        text = self._format_text(text)
        text_html = endline + '    '*(parent_depth + 1) + f'{tags[0]}' + endline
        text_html += f'{text}' + endline
        text_html += '    '*(parent_depth + 1) +f'{tags[1]}' + self._end + endline

        return text_html


class Quote(Text):

    def __init__(self, text, parent=None, font_size=16, alignment='left',
                 end=''):

        if not _Context._loading_from_json:
            grid = pr.containers.Grid(1,1)
        else:
            grid = parent

        Text.__init__(self, text, parent, font_size, alignment, end)
        pr.objects._Node.__init__(self, grid)


class PDF(_Node):

  '''
  Given an address for a pdf file, this will embed it inside the report.
  '''

  def __init__(self, pdf_path, parent=None, width=None, height=None,  end='<br>',
               style=''):

      pr.objects._Node.__init__(self, parent)
      if width is not None: assert isinstance(width, int), f'width should be int but is {type(width)}'
      if height is not None: assert isinstance(height, int), f'width should be int but is {type(width)}'

      self._pdf_path = pdf_path
      self._end = end
      self._width = width
      self._height = height
      self._style = style

  def _generate_html(self):

      pdf_html = '<br>'
      w = ""
      h = ""
      parent_depth = self._parent._depth

      if isinstance(self._parent, pr.containers.Section):
          indent = '    '*(parent_depth + 1)
      else:
          indent = '    '*(parent_depth)

      if self._width is not None:
        w = f"width=\"{self._width}\""
      if self._height is not None:
        h = f"height=\"{self._height}\""

      pdf_html += '\n' + indent + f'<embed src="{self._pdf_path}" {w} {h} type="application/pdf" style="{self._style}">'


      pdf_html +=  self._end + '\n'


      return pdf_html



class AcMap(_Node):

    '''
    Given the html for an antigenic cartography map, this embeds the map into
    the report.
    '''

    def __init__(self, acmap, parent=None, width=None, height=None, xscale=1,
                 yscale=1, end='<br>'):

        pr.objects._Node.__init__(self, parent)
        if width is not None: assert isinstance(width, int), f'width should be int but is {type(width)}'
        if height is not None: assert isinstance(height, int), f'width should be int but is {type(width)}'
        assert isinstance(xscale, (int,float)), f'xscale should be numeric but is {type(xscale)}'
        assert isinstance(yscale, (int,float)), f'scale should be numeric but is {type(yscale)}'

        self._acmap = acmap
        self._end = end
        self._width = width
        self._height = height
        self._xscale = xscale
        self._yscale = yscale


    def _generate_html(self):

        with open(self._acmap) as fp:
            lines = ''.join(fp.readlines())

        html_tokens = _internal.html_tokenizer(lines)

        body_html = html_tokens['body']
        for token in html_tokens['head']:
            if  token not in self._root()._CONFIG['SCRIPTS']['USER SCRIPTS']:
                self._root()._CONFIG['SCRIPTS']['USER SCRIPTS'] += '    ' + token.strip('\n') + '\n'


        I = _re.search(r'style="width:\d*px;height:\d*px',body_html)
        i0,i1 = I.span()
        dimensions = [int(float(x.split(':')[1].replace('px',''))) for x in body_html[i0+7:i1].split(';')]

        if self._width is not None:
            width = int(self._xscale*self._width)
        else:
            width = int(self._xscale*dimensions[0])

        if self._height is not None:
            height = int(self._yscale*self._height)
        else:
            height = int(self._yscale*dimensions[1])

        body_html = body_html.replace('"fill":true','"fill":false')

        body_html = _re.sub(r'"browser":{"width":\d*,"height":\d*,',f'"browser":{{"width":{width},"height":{height},',body_html)

        return body_html + self._end +'\n'


class Plot(_Node):

    '''
    Given the html for a plotly plot, it retrieves the necessary scripts from the
    head and the body of the html to embed it in the report.

    Although width and height can be changed via this function, there does not
    seem to be a uniform way that this is encoded in plotly plots so it is not
    guaranteed to work correctly so it is better to do it during creating the
    plotly plot itself.

    If you want to include the same plot twice in the same page, you should
    change its id by setting change_id = True

    '''

    def __init__(self, plot, parent=None,  width=None, height=None, xscale=1,
                 yscale=1, end='<br>', change_id=False):

        pr.objects._Node.__init__(self, parent)

        self._plot = plot
        self._end = end
        self._width = width
        self._height = height
        self._xscale = xscale
        self._yscale = yscale
        self._change_id = change_id


    def _generate_html(self):

        if isinstance(self._plot, str):
            with open(self._plot) as fp:
                lines = ''.join(fp.readlines())

        else:
            lines = _plotly.io.to_html(self._plot)

        html_tokens = _internal.html_tokenizer(lines)

        if self._change_id:
            # Note that if you try to include the same plotly plot twice in the same document,
            # it will fail unless it is div-id is changed. This is what this part does.
            # However doing this for many non-identical plots might be slow
            # and unneeded. So you can turn this off if needed.

            div_id = _re.search(r'(<div id=".*")|(<div class="plotly-graph-div" id="[^"]*")'
                                ,html_tokens['body']).group().split('"')[-2]

            new_id = ''.join(_rand.choice(_str.ascii_uppercase + _str.ascii_lowercase + _str.digits) for _ in range(16))

            html_tokens['body'] = html_tokens['body'].replace(div_id,new_id)

        for token in html_tokens['head']:
            if '<meta' not in token and '<style' not in token and token not in self._root()._CONFIG['SCRIPTS']['USER SCRIPTS']:
                self._root()._CONFIG['SCRIPTS']['USER SCRIPTS'] += '    ' + token.strip('\n') + '\n'

        div_html = html_tokens['body'] + self._end + '\n'

        if self._height is not None or self._width is not None or self._xscale != 1 or self._yscale != 1:
            I = _re.search(r'class="plotly-graph-div" style="height:.*px; width:.*px;',html_tokens['body']).group()
            I = _re.search(r'height:.*px; width:.*px',I).group()
            dimensions = [x.split(':')[1].replace('px','') for x in I.split(';')]
            num_dimensions = [float(x) for x in dimensions]

            if self._width is not None:
                width = int(self._xscale*self._width)
            else:
                width = int(self._xscale*num_dimensions[1])

            if self._height is not None:
                height = int(self._yscale*self._height)
            else:
                height = int(self._yscale*num_dimensions[0])

            div_html = div_html.replace(f'"width":{dimensions[1]}',f'"width":{width}')
            div_html = div_html.replace(f'"height":{dimensions[0]}',f'"height":{height}')

        return div_html


class Image(_Node):

    """
    Image object: It can either accept a str as image input which should be the
    path of the saved image, or a matplot lib figure object. If width and height
    is not given as input, width and height of the original image is used and scaled
    by scale.

    If embed is True, then the image is embedded to the html document by converting
    it to bytes. In such a case you don't need to keep a copy of the figure to
    load it to the report. Text is the title that will be displayed

    It is not meant to be initialized from scratch but should be called from a Section object
    """

    def __init__(self, image, parent=None, width=None, height=None, title=None, scale=1,
                 embed=True, style=None, end='<br>'):

        pr.objects._Node.__init__(self, parent)

        if width is not None and height is not None:
            assert  width>0 and height>0,f'Width and height should be positive but they are {width} and {height}'
        else:
            if isinstance(image,(str,PosixPath)):
                with open(str(image), "rb") as fp:
                  pimage = _PIL.Image.open(fp)

                width, height = pimage.size
            elif image is None:
                if width is None:
                    width = 0
                if height is None:
                    height = 0
                pimage = _PIL.Image.new('RGB', (width,height))
                width, height = pimage.size
            elif isinstance(image, _mpl.figure.Figure):
                width, height = image.get_size_inches()*image.dpi
            elif isinstance(image, _PIL.Image.Image):
                width, height = image.size
            else:
                raise ValueError(f'image should be str or mpl figure but is {type(image)}')

            width *= scale
            height *= scale


        if title is not None:
            assert isinstance(title,str), 'title should be a str'
        else:
            title = ''
        if style is not None:
            assert isinstance(style,str), 'style should be a str'
        else:
            style = ''

        self._image = image
        self._width = width
        self._height = height
        self._embed = embed
        self._title = title
        self._scale = scale
        self._end = end
        self._style = style


    def _generate_html(self):

        img_html = '<br>'
        parent_depth = self._parent._depth

        if isinstance(self._parent, pr.containers.Section):
            indent = '    '*(parent_depth + 1)
        else:
            indent = '    '*(parent_depth)

        if self._title == '':
            title_str = ''
        else:
            title_str = f'{self._title}<br>'

        if self._embed:

            if isinstance(self._image, (str,PosixPath)):
                with open(str(self._image), 'rb') as fp:
                    img_bytes = fp.read()

                if self._width is None and self._height is None:
                    pimage = _PIL.Image.open(self._image)
                    width, height = pimage.size
            elif isinstance(self._image, _mpl.figure.Figure):
                img = _internal.fig2img(self._image)
                img_bytes = _internal.image_to_byte_array(img)

                if self._width is None and self._height is None:
                    width, height = self._image.get_size_inches()*self._image.dpi
            elif isinstance(self._image, _PIL.Image.Image):
                img = self._image
                img_bytes = _internal.image_to_byte_array(img)
            elif self._image is None:
                img_bytes = b''
            else:
                raise ValueError(f'An embeddable image must either be a maplot image object or a path to an image but was instead {type(self._image)}')

            self._base64_img = _b64.b64encode(img_bytes).decode("utf-8")#

            img_html += '\n' + indent + f'{title_str}<img src="data:image/png;base64,{self._base64_img}" title="{self._title}" width="{self._width}" height="{self._height}" style="{self._style}">'
        else:
            assert isinstance(self._image,str), 'If not embedded image input should be the path of the image'

            img_html += '\n' + indent + f'{title_str}<img src="{self._image}" width="{self._width}" height="{self._height}" style="{self._style}">'

        img_html +=  self._end + '\n'


        return img_html


class Table(_Node):
    """
    """
    def __init__(self, table, background_colors=None, parent=None,
                 header_style=None, row_style=None, cell_colors=None):

        pr.objects._Node.__init__(self, parent)

        if header_style is None:
          header_style = ''
        if row_style is None:
          row_style = ''
        if background_colors is None:
          background_colors = [None for _ in range(table.shape[0])]
        else:
          if len(background_colors) != table.shape[0]:
            raise ValueError('length of background colors should be equal to '
                             'number of rows of the table')
        if cell_colors is None:
          cell_colors = [[None for _ in range(table.shape[1])]
                         for _ in range(table.shape[0])]
        else:
          if (len(cell_colors) != table.shape[0] or not
              all(len(x)==table.shape[1] for x in cell_colors)):
            raise ValueError('cell_colors must be a list of length equal to '
                             'number of rows of the table and each element of the '
                             'list must also be a list of length equal to number '
                             'of columns of the table'
                             )

        self._table = table
        self._background_colors = background_colors
        self._row_style = row_style
        self._header_style = header_style
        self._cell_colors = cell_colors

    def _generate_html(self):

        table_html = '\n'
        parent_depth = self._parent._depth

        if isinstance(self._parent, pr.containers.Section):
            indent = '    '*(parent_depth + 1)
        else:
            indent = '    '*(parent_depth)

        table_html += indent + '<table class="sortable">\n\n'
        table_html += '\n'.join([indent + '  ' + x for x in self._generate_colnames_html(self._table.columns, self._header_style).split('\n')]) + '\n\n'
        table_html += indent + '  <tbody>\n'

        for bcolor,ccolors, row in zip(self._background_colors,
                                      self._cell_colors,
                                      self._table.iterrows()):
          row_style = self._row_style
          cell_styles = []

          if bcolor is not None:
              row_style += f'background-color:{bcolor}'

          cell_styles = [f'background-color:{ccolor}' if ccolor is not None
                         else '' for ccolor in ccolors]

          table_html += '\n'.join([indent + '  ' + x for x in self._generate_row_html(row[1], row_style, cell_styles).split('\n')]) + '\n'

        table_html += indent + '  </tbody>\n\n'

        table_html += indent + '</table>'

        return table_html

    def _generate_colnames_html(self, col_names, style=''):

        colnames_html = f'<thead>\n  <tr style="{style}">\n'

        for elem,td_class in zip(col_names, self._classes):
          if 'num' in td_class:
            just = '"text-align:right;"'
          else:
            just = '"text-align:left;"'

          colnames_html += f'    <th {td_class}><button style={just}>{elem}<span aria-hidden="true"></span></button></th>\n'

        colnames_html += '  </tr>\n</thead>'

        return colnames_html


    def _generate_row_html(self, row, row_style, cell_styles):

        row_html = f'  <tr style="{row_style}">\n'

        for elem,cell_style,td_class in zip(row, cell_styles, self._classes):

          row_html += f'   <td {td_class}style="{cell_style}">{elem}</td>\n'

        row_html += '  </tr>'

        return row_html

    @property
    def _classes(self):

        classes = []
        for i in range(self._table.shape[1]):
            col_vals = self._table.iloc[:,i]
            classes.append(_internal._class(col_vals))

        return classes
