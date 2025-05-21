#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 13:28:59 2022

@author: Sina Tureli

"""

import re as _re
import os as _os

from bs4 import BeautifulSoup as _bs
from . import config
from . import objects
from pathlib import Path, PosixPath

_NoneType = type(None)
cdir = _os.path.dirname(__file__)
css_dir = _os.path.join(cdir, 'config/css')

class _Container(objects._Context, objects._Node):

    '''
    Base class from which all the specialized classes in this module
    derive from
    '''

    def __init__(self, parent=None):

        objects._Context.__init__(self)
        objects._Node.__init__(self, parent)


    @property
    def _has_tab(self):
        '''

        Returns
        -------
        bool
            Whether or not any of its subcontainers has tabs in them

        '''

        return self._has('_tabs')


    @property
    def _has_grid(self):
        '''

        Returns
        -------
        bool
            Whether or not any of its subcontainers has grids in them

        '''

        return self._has('_grids')


    @property
    def _has_code(self):
        '''

        Returns
        -------
        bool
            Whether or not any of its subcontainers has code in them

        '''

        return self._has('_codes')


    @property
    def _has_table(self):
        '''

        Returns
        -------
        bool
            Whether or not any of its subcontainers has tables

        '''

        return self._has('_tables')


    @property
    def _has_fold(self):
        '''

        Returns
        -------
        bool
            Whether or not any of its subcontainers has folds in them

        '''

        return self._has('_folds')


    @property
    def _tabs(self):
        '''

        Returns
        -------
        tabs : list
            list of tabs in this container

        '''

        tabs = self._items('tab')

        return tabs


    @property
    def _folds(self):
        '''

        Returns
        -------
        folds : list
            list of folds in this container

        '''

        folds = self._items('fold')

        return folds


    @property
    def _tables(self):
        '''

        Returns
        -------
        folds : list
            list of tables in this container

        '''

        tables = self._items('table')

        return tables


    @property
    def _grids(self):
        '''

        Returns
        -------
        grids : list
            list of grids in this container

        '''

        grids = self._items('grid')

        return grids


    @property
    def _codes(self):
        '''

        Returns
        -------
        folds : list
            list of codes in this container

        '''

        codes = self._items('code')

        return codes


    def _has(self, item):

        '''

        Returns
        -------
        bool
            Whether or not any of its subcontainers has the given item in them

        '''
        return len(self.__getattribute__(item))>0


    def _items(self, item_name):

        '''

        Returns
        -------
        items : list
            list of given items in this container

        '''
        if item_name == 'code':
            item_class = objects.Code
        elif item_name == 'table':
            item_class = objects.Table
        elif item_name == 'tab':
            item_class = Tab
        else:
            class_name = item_name.capitalize()
            item_class = globals()[class_name]

        items = []
        for descendant in self._descendants():
            if isinstance(descendant, item_class):
                items.append(descendant)

        return items


class Report(_Container):
    '''

    children of _Context and _Node

    A report object inherits from Node and has the form of a tree with the
    report object as the root. The tree structure is for simple book keeping
    and formatting the html code for the report so that it is easy on the eyes.

    Attributes and properties
    ----------
    title()
    pretext()
    section()
    sections
    to_html()
    _has_tex
    _title_html
    _add_styles()
    _add_scripts()

    _title : title of the report
    _pretext: pretext that is shown before the title (such as links at the top)
    _meta: meta tag of the html file, see __init__ for default value
    _CONFIG: initialized via the config module, contains style and scripts for html
             see user.ini for changing the default values

    '''
    def __init__(self, title: str, title_style: str=None, meta: str=None,
                 pretext: str=None, update_config_name: str='user'):
        '''

        Constructor

        Parameters
        ----------
        title : str
            Title of the report
        title_style : str, optional
            html title style for the title ex: 'color:black;font-size:14px'
            defaults to ''
        meta : str, optional
            the meta info of the html. defaults to
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        pretext : str, optional
            the pretext that appears before the report title (such as links at the top).
            defaults to ''
        update_config_name: str, optional, default 'user'
            which config file to update the default.ini. The file should be placed
            inside the config folder
        '''

        _Container.__init__(self)

        self._check_types(['title','title_style','meta','pretext'],
                          [title,title_style,meta,pretext],
                          [str,(str,_NoneType),(str,_NoneType),(str,_NoneType)],
                          '__init__')

        if meta is None:
            meta = '<meta name="viewport" http-equiv="Content-Type" content="text/html; charset=utf-8"">\n'
        if pretext is None:
            pretext = ''
        if title_style is None:
            self._title_style = ''


        self._title = title
        self._pretext = pretext
        self._meta = meta
        self._update_config_name = update_config_name
        self._CONFIG = config.load_config(update_config_name)
        # this loads the html style and script
        # parameters. Addition of certain objects
        # like maps or plotly plots might modify the
        # CONFIG further since these come with their
        # own lengths injected scripts


    def title(self, title, title_style=None):
        '''

        In case you want to change report title and its style, potentially useful
        when loading a previous report from json to reuse or as a template
        and need to change section titles.

        Parameters
        ----------
        title : str
            new title for the report

        title_style : str, optional
            html title_style, ex: "color:black;font-size:12px"
            defaults to ''

        Returns
        -------
        None.

        '''

        self._check_types(['title','title_style'],
                          [title,title_style],
                          [str,(str,_NoneType)],
                          'title')

        self._title = title

        if title_style is None:
            self._title_style = ''
        else:
            assert isinstance(title_style,str), 'title style must be a string'
            self._title_style = title_style


    def pretext(self, pretext):
        '''
        Parameters
        ----------
        pretext : str
            the pretext, see __init__ for details

        Returns
        -------
        None.

        '''

        self._check_types('pretext',pretext,str,'pretext')
        self._pretext = pretext


    @property
    def sections(self):
        '''

        Returns
        -------
        list
            A list of sections in the report (does not return subsections of sections)

        '''

        return [x for x in self._children if isinstance(x,Section)]


    def to_html(self, output_path: str|PosixPath, return_html: bool=False):
        '''

        Parameters
        ----------
        output_path : str
            path to save the report
        return_html : bool, optional
            whether or not to return the generated html as a string. The default is False.

        Returns
        -------
        html : str
            if return_html is True, this is the returned html string.

        '''

        self._check_types(['output_path','return_html'],
                          [output_path, return_html],
                          [(str, PosixPath), bool],'to_html')

        head_html = '<!-- Report generated by PyReports (author: Sina Tureli). -->\n\n'
        head_html += '<!DOCTYPE html>\n<html>\n'
        head_html += '<head>\n'
        body_html = ''

        if self._pretext != '':
            body_html += '<pre>' + self._pretext + '</pre>\n'

        if self._has_tab:
            body_html += '\n<body onload=\"open_defaults(\'tabcontent\')\">\n'
        else:
            body_html += '\n<body>\n'

        body_html += self._title_html

        if len(self.sections)>0:
            summary = str(self.summary(link_to_sections=True))
            summary = summary.replace('SUBSUBSECTION (','').replace('SUBSECTION (','').\
              replace('SECTION (','').replace(')\n','\n')
            summary = '\n'.join(summary.split('\n')[1:])
            body_html += '<pre>\n' + summary + '</pre>\n'

        for ind,child in enumerate(self._children):

            body_html += child._generate_html()

        body_html += '</body>\n\n<!-- END REPORT -->\n</html>'

        head_html += '\n' + self._add_scripts()

        head_html += '\n'.join(self._add_styles())

        head_html += '</head>\n'

        html = head_html + body_html
        with Path(output_path).open('w') as file:
            file.writelines(html)

        if return_html:
            return html


    @property
    def _has_tex(self):
        '''
        Check if any of the sections contain tex strings, this is used
        to determine whether or not we should include scripts related to
        tex rendering.
        '''
        return any(x._has_tex for x in self.sections)


    @property
    def _title_html(self):
        '''
        Return the html code for the title (with commentary)
        and encode the style in it.
        '''

        return '\n<!-- START REPORT -->\n' + f'<h1 style = "{self._title_style}">{self._title}</h1>\n'



    def _add_styles(self):
        '''
        Generate relevant styles for the <head> of the html, called during report
        rendering.
        '''

        CONFIG = self._CONFIG

        tab_styles = CONFIG['STYLES']['TAB STYLES']
        grid_styles = CONFIG['STYLES']['GRID STYLES']
        body_style = CONFIG['STYLES']['BODY STYLE']
        h_styles = CONFIG['STYLES']['H STYLES']
        p_style = CONFIG['STYLES']['P STYLE']
        img_style = CONFIG['STYLES']['IMG STYLE']
        user_styles = CONFIG['STYLES']['USER STYLES']
        code_style = CONFIG['STYLES']['CODE STYLE'].lstrip(' ')
        fold_styles = CONFIG['STYLES']['FOLD STYLES']
        table_styles = CONFIG['STYLES']['TABLE STYLES']
        #  add head with styles
        style_html = ['\n    <style>']

        style_html += [body_style, img_style, h_styles, p_style, user_styles]

        if self._has_tab:
            style_html += [tab_styles]

        if self._has_grid:
            style_html += [grid_styles]

        if self._has_fold:
            style_html += [fold_styles]

        if self._has_table:
            style_html += [table_styles]


        if self._has_code:
          code_style_css_path = _os.path.join(css_dir,f'{code_style}.css')

          with open(code_style_css_path, "r") as fp:
            code_style_css = '\n'.join(map(lambda x: f"    {x}", fp.readlines()))


          style_html.append(code_style_css)

        style_html += ['    </style>\n']

        return style_html


    def _add_scripts(self):
        '''
        Generate relevant scripts for the <head> of the html, called during report
        rendering.
        '''

        scripts_html = f'    {self._meta}'
        CONFIG = self._CONFIG

        if self._has_tab:
            scripts_html +=  CONFIG['SCRIPTS']['TAB SCRIPT']

        if self._has_tex:
            scripts_html += CONFIG['SCRIPTS']['TEX SCRIPT']

        if self._has_code:
            scripts_html += CONFIG['SCRIPTS']['CODE SCRIPT']

        if self._has_fold:
            scripts_html += CONFIG['SCRIPTS']['FOLD SCRIPT']

        if self._has_table:
            scripts_html += CONFIG['SCRIPTS']['TABLE SCRIPT']

        scripts_html += CONFIG['SCRIPTS']['USER SCRIPTS']

        return scripts_html


class Section(_Container):
    '''
    children of _Context and _Node

    Attributes
    ----------
    title()
    sections()
    _is_subsection
    _section_no
    _section_no_str
    _title_html
    _nitems
    _generate_html()

    _has_tex: whether or not this section contains tex
    _has_code: whether or not this section contains code

    _title: title of the section

    '''

    def __init__(self, title, title_style = None, has_tex=False, parent=None):
        '''
        Parameters
        ----------
        title : str
            Title of the section.
        title_style : str, optional
            html style for the section_title. It defaults to ''
        has_tex : bool, optional
            Should be True if you include tex to be rendered. Any tex formulas
            should be wrapped between $$. The default is False.
        parent : bool, optional
            Parent of this section (another Section or Report) if it exists.
            If None, _Node() initialization tries to get it from context.
            If there is not context, will produce an error so you can not create
            a section without a parent or a context. As an example:

                report = Report('report title')
                section = Section('section title',report)

            or with context:

                with Report('report title'):
                    with Section('section title'):
                        #add other stuff

            The second method is the preferred method, the first method is
            what works under the hood when second method is used (+ some context
            management).


        Returns
        -------
        None.

        '''

        _Container.__init__(self, parent)

        self._check_types(['title','title_style','has_tex','parent'],
                                  [title, title_style, has_tex, parent],
                                  [str, (str,_NoneType), bool, (objects._Node,_NoneType)],
                                  '__init__')

        if title_style is None:
            self._title_style = ''
        else:
            self._title_style = title_style

        self._has_tex = has_tex
        self._title = title


    def title(self, title, title_style=None):
        '''
        Change the title and title_style of the report.

        Parameters
        ----------
        title : str
            New title for the report.
        title_style : str, optional
            html style for the title. Defaults to ''

        Returns
        -------
        None.

        '''

        self._check_types(['title','title_style'],
                                  [title,title_style],
                                  [str,(str,_NoneType)],
                                  'title')

        self._title = title

        if title_style is None:
            self._title_style = ''


    @property
    def sections(self):
        '''

        Returns
        -------
        list
            List of subsections of the section (but subsubsections of subsections
            are not included).

        '''

        return [x for x in self._children if isinstance(x,Section)]


    @property
    def _is_subsection(self):
        '''

        Returns
        -------
        bool
            Whether or not this is a subsection of another section

        '''

        return isinstance(self._parent,Section)


    @property
    def _section_no(self):
        '''

        Returns
        -------
        section_no : int
            Index of this section with in the subsections of its parent

        '''

        if self._parent is None:
            section_no = 1
        else:
            section_no = self._parent.sections.index(self) + 1

        return section_no


    @property
    def _section_no_str(self):
        '''

        Returns
        -------
        section_no_str : str
            Complete section number, so for instance this is subsection 2
            of section 1 then it is 1.2. Used in section titles for both
            html code organization and for the actual rendered page.

        '''

        section_no_str = str(self._section_no)
        parent = self._parent

        while isinstance(parent,Section):
            parent_section_no = parent._section_no
            section_no_str = f'{parent_section_no}.{section_no_str}'
            parent = parent._parent


        return section_no_str


    @property
    def _title_html(self):
        '''

        Returns
        -------
        title_html : str
            The title str for the section used in the html with some commentes
            and the title_style included.

        '''

        depth = self._depth

        if depth>5:
            htag = 'h6'
        else:
            htag = f'h{depth+1}'

        title_html = f'<{htag} style = "{self._title_style};">{self._title}</{htag}>\n'

        return title_html


    @property
    def _nitems(self):
        '''

        Returns
        -------
        nitems : int
            Total number of tab items with in this section
            (extends to sub...subsections).

        '''

        nitems = 0

        for child in self._children:
            if isinstance(child,Tab):
                nitems += len(child._children)
            elif isinstance(child,Section):
                nitems += child._nitems

        return nitems


    def _generate_html(self):
        '''

        Returns
        -------
        section_html : str
            The html code that represents the contents of this section.
            Called when the parent containing this section is generating
            its html code (either the parent Section's _generate_html()
                           or the parent Report' to_html() methods)

        '''

        title_html = self._title_html

        if not self._is_subsection:
            section_type = 'SECTION'
            border = 'solid'
        else:
            section_type = 'SUBSECTION'
            border = 'solid'

        section_html = ''

        depth = self._depth

        hr_index = depth
        if hr_index>3: hr_index=3

        section_html += '\n' + '    '*depth + f'<!-- START {section_type} {self._section_no_str} -->\n'
        section_html += '\n' + '    '*depth + f'<div id="S{self._section_no_str}">'
        section_html += '    '*depth + f'<section style="margin-left:{20*depth}px; margin-bottom:10px; border-left:{border}; padding-left:10px">\n'
        section_html += '    '*depth + f'{title_html}\n'


        for ind,child in enumerate(self._children):

            html =  child._generate_html()

            if isinstance(child, Section) and child._has_tex:
                html = html.replace('\n','<br>\n')

            section_html += html

        section_html += '\n' + '    '*depth + '<div>'
        section_html += '    '*depth + '</section>\n'
        section_html += '\n'+'    '*depth + f'<!-- END {section_type} {str(self._section_no_str)} -->\n'

        return section_html


class Tab(_Container):
    '''
    Represent stuff in tab format. Also aimed to be used with context manager as such:

        with Tab(['Tab1','Tab2']):
            [Image(x) for x in ['path1.png','path2.png']]

    '''

    def __init__(self, tab_titles, tab_style=None, button_styles=None, content_styles=None,
                 end='<br><br>', parent=None):

        _Container.__init__(self, parent)

        self._end = end
        self._tab_style = tab_style
        self._button_styles = button_styles
        self._content_styles = content_styles
        self._tab_titles = tab_titles


    def add_object(self, obj):

        assert isinstance(obj, objects._Node)

        if obj._parent != self:
            obj._parent = self


    @property
    def _nitems(self):

        return len(self._children)


    @property
    def _root_section(self):

        parent = self._parent

        while isinstance(parent._parent, Section) or not isinstance(parent, Section):
            parent = parent._parent

        return parent


    @property
    def _tab_item_ids(self):

        report_tabs = self._root()._tabs
        try:
          I = report_tabs.index(self)
        except:
          breakpoint()
        ntabs = sum([len(x._children) for x in report_tabs[:I]])

        return [ntabs + i for i in range(len(self._children))]


    @property
    def _tab_name(self):
        # class ids are required for open all and close buttons
        # each tab that is given a class name so that the script
        # which opens and closes tabs can supplied this class and
        # closes or opens only items from the tab which has the given
        # class name

        return f'TAB-{self._root_section._section_no_str}-{self._root_section._tabs.index(self)}'


    @property
    def _styles(self):

        if self._tab_style is None:
            tab_style = ''
        else:
            tab_style = f' style="{self._tab_style}"'

        if self._button_styles is None:
            button_styles = ['']*self._nitems
        else:
            if not isinstance(self._button_styles,list):
                button_styles = [self._button_styles]*self._nitems
            else:
                button_styles = self._button_styles


            button_styles =[f' style="{x}"' for x in button_styles]

        return tab_style, button_styles


    def _generate_html(self):

        if len(self._tab_titles) != self._nitems:
            raise ValueError(f'Number of tab titles {len(self._tab_titles)} does not match number of items {self._nitems} for {repr(self)}')

        tab_style, button_styles = self._styles

        tab_html = ''
        indent = '    '*(self._parent._depth + 1)

        item_ids = self._tab_item_ids
        tab_name = self._tab_name

        tab_html += '\n' + indent + f'<!-- START {tab_name} -->\n'

        tab_html += indent + f'<br><div class="tab" {tab_style}>\n'

        for i in range(len(self._children)):

            if i==0:
                name='name="default_open" '
            else:
                name=''

            tab_html += '    ' + indent + f'<button class="tablinks" {name}style="{button_styles[i]}" onclick="open_tab(event, \'{item_ids[i]}\',\'{tab_name}\' )"><strong>{self._tab_titles[i]}</strong></button>\n'

        #open all button also know as Derek button
        if len(self._children)>0:
            tab_html += '    ' + indent + f'<button class="tablinks" style="{button_styles[i]}" onclick="open_all_tabs(event, \'{tab_name}\')"><strong>Open All</strong></button>\n'

        tab_html += indent + '</div>\n'

        for i in range(len(self._children)):

            if i==0:
                display_style = 'style="display:block"'
            else:
                display_style = ''


            tab_html += indent + f'<div id="{item_ids[i]}" {display_style} class="tabcontent" name="{tab_name}">\n'
            tab_html += '    ' + indent + '<span onclick="this.parentElement.style.display=\'none\'" class="topright">x</span>\n'
            tab_html += self._children[i]._generate_html()

            tab_html += indent + '</div>\n'

        tab_html += indent + f'{self._end}' + '\n'
        tab_html += indent + f'<!-- END {tab_name} -->\n'

        return tab_html


class Fold(_Container):
    '''
    Represent stuff inside a foldable section. Also aimed to be used with context manager as such:

        with Fold():
            Txt('Some text')

    '''

    def __init__(self, collapsible_style=None, button_style=None, content_style=None,
                 end='<br><br>', parent=None):

        _Container.__init__(self, parent)

        self._end = end
        self._collapsible_style = collapsible_style
        self._button_style = button_style
        self._content_style = content_style


    def add_object(self, obj):

        assert isinstance(obj, objects._Node)

        if obj._parent != self:
            obj._parent = self


    @property
    def _root_section(self):

        parent = self._parent

        while isinstance(parent._parent, Section):
            parent = parent._parent

        return parent


    @property
    def _styles(self):

        if self._collapsible_style is None:
            collapsible_style = ''
        else:
            collapsible_style = f' style="{self._tab_style}"'

        if self._button_style is None:
            button_style = ''
        else:
            if not isinstance(self._button_style, list):
                button_style = self._button_style
            else:
                button_style = self._button_style


        return collapsible_style, button_style


    @property
    def _fold_name(self):
        return f'FOLD-{self._root_section._section_no_str}-{self._root_section._folds.index(self)}'


    def _generate_html(self):

        tab_style, button_style = self._styles

        fold_html = ''
        indent = '    '*(self._parent._depth + 1)

        fold_name = self._fold_name

        fold_html += '\n' + indent + f'<!-- START {fold_name} -->\n'

        fold_html += '    ' + indent + f'<button type="button" style="{button_style}" class="fold" onclick="click_fold(this)"></button>\n'

        fold_html += '    '*2 + indent + '<div class="foldcontent">\n'

        for i in range(len(self._children)):
            fold_html += self._children[i]._generate_html()

        fold_html += '    '*2 + indent + f'</div>{self._end}\n'

        fold_html += indent + f'<!-- END {fold_name} -->\n'

        return fold_html


class Grid(objects._Context,objects._Node):
    '''
    A grid is used when the user wants to show a grid of images
    or other objects. The specialized grid types ImageGrid,
    PlotlyGrid, MapGrid derive from this.
    '''

    def __init__(self, ncols, nrows=1, item_titles:list=None,
                 grid_style:str=None, grid_item_styles:list=None, end='<br><br>',
                 parent=None, fontsize=16, fontweight="bold"):

        objects._Node.__init__(self, parent)

        if nrows is None and ncols is None:
            raise ValueError('you must supply either nrows or ncols')
        else:
            assert isinstance(nrows,int), f'nrows should be an integer but is {type(nrows)}'
            assert isinstance(ncols,int), f'ncols should be an integer but is {type(ncols)}'

        if item_titles is not None:
            if isinstance(item_titles,str):
                item_titles = [item_titles]
            assert len(item_titles) == ncols*nrows, f'nrows*ncols is {ncols*nrows} but {item_titles} are supplied as titles which has length {len(item_titles)}.'

        if grid_style is None:
            grid_style = ''
        else:
            assert isinstance(grid_style,str), 'grid style must be a string'

        if grid_item_styles is None:
            grid_item_styles = ['']*(nrows*ncols)
        else:
            assert all(isinstance(x,str) for x in grid_item_styles), 'grid_item_styles must be a list of strings'
            assert len(grid_item_styles) == nrows*ncols, 'grid_item_styles must have same number of elements as ncols*nrows'


        self._end = end
        self._nrows = nrows
        self._ncols = ncols
        self._grid_style = grid_style
        self._grid_item_styles = grid_item_styles
        self._item_titles = item_titles
        self._fontsize = fontsize
        self._fontweight = fontweight

    def _generate_html(self):

        cols = 'auto '*self._ncols
        rows = 'auto '*self._nrows
        indent = '    '*(self._parent._depth + 1)
        grid_style = self._grid_style
        fontstyle =  f"<text style=\"font-size:{self._fontsize}px; font-weight:{self._fontweight};\">"


        if len(self._children)>self._ncols*self._nrows:
            raise ValueError(f'{repr(self)} has {len(self._children)} children but nrows*ncols is {self._nrows*self._ncols}')

        if isinstance(self._parent, Grid):
            grid_style += 'padding:0px'

        html =''
        html += '\n' + indent + '<!-- START GRID -->\n'
        html += indent + f'<div class="grid-container" style="grid-template-columns: {cols}; grid-template-rows: {rows}; {grid_style}">\n'

        for ind_child,child in enumerate(self._children):
            child_html_str = child._generate_html()
            child_html_str = _re.sub('(\/n)*$', '', child_html_str).strip('\n')
            child_style = self._grid_item_styles[ind_child]

            if isinstance(child, objects.Text):
                soup = _bs(child_html_str, 'html.parser')
                text = _bs.get_text(soup).strip('\n').strip(' ')
                if len(text)==0:
                    child_style += 'background-color: inherit;'

            if self._item_titles is not None:
                child_html_str = fontstyle + self._item_titles[ind_child] + '</text>' + child_html_str

            if isinstance(self._parent, Grid):
                child_style += 'padding:0px;'

            html += indent + '    ' + f'<div class="grid-item" style="{child_style}">{child_html_str}</div>\n'

        html += indent + f'</div>{self._end}\n'
        html += indent + '<!-- END GRID -->\n'


        return html
