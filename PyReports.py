#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 20:03:19 2020

@author: avicenna
"""
import base64
from PIL import Image, ImageFont
import matplotlib
import io
import importlib
import os

module_path = os.path.dirname(os.path.abspath( __file__ ))

def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

def image_to_byte_array(image:Image):
    """Convert an Image to byte like array without saving to disk"""
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

class ReportText:

    """Text object: Can define font size and alignment of text with inputs.
    _to_html generates a string which defines the html code that will display the
    text as an html object.
    """

    def __init__(self,text, font_size=16, alignment='left'):

        assert alignment in ['left','right','center'], 'alignment should be left right or center'
        assert isinstance(text,str),'Text should be a str'
        assert isinstance(font_size, (float,int)), 'Font size should be numeric'
        assert font_size>0, 'Font size should be larger than 0'

        self.text = text
        self.font_size = font_size
        self.alignment = alignment

    def _to_html(self):

        return ['\t<p style = "font-size:' + str(self.font_size) + 'px; ' + 'text-align:' + self.alignment + '" >','\t\t' + self.text,'\t</p>\n']

class ReportImage:

    """Image object: It can either accept a str as image input which should be the
    path of the saved image, or a matplot lib figure object. If width and height
    is not given as input, width and height of the original image is used.

    If embed is True, then the image is embedded to the html document by converting
    it to bytes. In such a case you don't need to keep a copy of the figure to
    load it to the report. Text is the caption that will be displayed """

    def __init__(self, image, width=None, height=None, alignment='right', embed=True, caption=None):

        assert isinstance(image,str) or isinstance(image, matplotlib.figure.Figure),'Images should be either in str format or matplotlib figure format but is {} instead'.format(type(image))
        assert isinstance(embed, bool), 'embed parameter should be bool but it is {}'.format(type(embed))
        assert isinstance(alignment, str), 'alignment parameer should be str but it is {}'.format(type(caption))

        if width is not None and height is not None:
            assert int(width)==width and int(height)==height and width>0 and height>0,'Width and height should be positive integers but they are {} and {}'.format(width,height)
        else:
            assert width is None and height is None, 'Width and height should be both initialized.'

        assert alignment in ['left','right','beforeright'], 'alignment should be left or right but it is {}'.format(alignment)

        if caption is not None:
            assert isinstance(caption,str), 'Caption should be a str'

        self.image = image
        self.width = width
        self.height = height
        self.embed = embed
        self.alignment = alignment
        self.caption = caption

    def _to_html(self):

        img_html = []
        img_html.append('\t<figure class="' + self.alignment + '">')

        if self.embed:
            if isinstance(self.image, str):
                img_bytes = open(self.image, 'rb').read()

                if self.width is None and self.height is None:
                    pimage = Image.open(self.image)
                    width, height = pimage.size

            elif isinstance(self.image, matplotlib.figure.Figure):
                img = fig2img(self.image)
                img_bytes = image_to_byte_array(img)

                if self.width is None and self.height is None:
                    width, height = self.image.get_size_inches()*self.image.dpi

            data_uri = base64.b64encode(img_bytes) #
            img_html.append('\t\t<img src="data:image/png;base64,{}" width="{}" height="{}">'.format(data_uri.decode("utf-8"), self.width, self.height))
        else:
            assert isinstance(self.image,str), 'If not embedded image input should be the path of the image'

            img_html.append('\t<img src="{}" width="{}" height="{}">\n'.format(self.image, self.width, self.height))

        if self.caption is not None:
            img_html.append('\t\t<figcaption>' + self.caption +'</figcaption>')

        img_html.append('\t</figure>\n')

        return img_html

class ReportList:

    def __init__(self, objects, is_ordered= False):

        assert isinstance(is_ordered,bool), 'is_oredered should be a bool but is {}'.format(type(is_ordered))
        assert isinstance(objects, list), 'objects should be a list but is {}'.format(type(objects))

        self.objects = objects
        self.is_ordered = is_ordered

    def _to_html(self):

        list_html = []

        if self.is_ordered:
            tag = 'ol'
        else:
            tag = 'ul'

        list_html.append('\t<' + tag + '>')

        for item in self.objects:
            list_html.append('\t\t<li>')
            list_html += ['\t\t' + x for x in item._to_html()]
            list_html.append('\t\t</li>')

        list_html.append('\t</' + tag + '>\n')

        return list_html

class ReportLink:

    def __init__(self, link_url, link_name=None):

        assert isinstance(link_url,str), 'Link url should be a str but is {}'.format(type(link_url))

        self.link_url = link_url

        if link_name is None:
            self.link_name = link_url

        else:
            assert isinstance(link_name,str), 'Link name should be a str but is {}'.format(type(link_name))
            self.link_name = link_name

    def _to_html(self):

        return ['\t<a href="' + self.link_url + '">' + self.link_name + '</a>\n']


class ReportSection:

    '''Section object can be created independently of the report and added to a
    report object. section_no is used to format the html file with section comment
    outs that contain the section no but otherwise has no function. Each section
    is divided hr.suphr divider line. Content can be added to sections with a
    list of add_ functions below.

    is_subsection: if True, then the divider line is finer than the section dividers.
    otherwise it does not require a parent section to be a created (see below the
    report section on how to add sections and subsections).
    '''

    def __init__(self, section_no, is_subsection=False):

        assert isinstance(section_no,(int, float, str)), 'section no should be an integer, float or str'
        assert isinstance(is_subsection, bool), 'is_subsection should be bool but it is {}'.format(is_subsection)

        self.section_no = section_no
        self.section_contents = []
        self.html = ''
        self.number_of_mtabs = 0
        self.is_subsection = is_subsection

        if self.is_subsection:
            self.hr_style = '"subhr"'
            self.name = 'SUBSECTION {}'.format(self.section_no)
        else:
            self.hr_style = '"suphr"'
            self.name = 'SECTION {}'.format(self.section_no)


        self.section_contents.append('<hr class='+self.hr_style+'>  <!--START OF ' + self.name + '-->\n')

    def add_section_title(self, title_text, color = "black", end='<br>'):

        assert isinstance(end,str), 'end should be a str but is {}'.format(type(end))
        assert isinstance(title_text,str),'Title text should be a str'

        if self.is_subsection:
            self.section_title = '\t<p><h2 style = "color: {}; text-align:left">{}</h2></p>{}\n'.format(color,title_text,end)

        else:
            self.section_title = '\t<p><h1 style = "color: {}; text-align:center">{}</h1></p>{}\n'.format(color,title_text,end)

        self.section_contents.append(self.section_title)
        self.section_contents.append('\t' + end)

    def add_list(self, objects, is_ordered=False, end='<br>'):
        assert isinstance(end,str), 'end should be a str but is {}'.format(type(end))

        self.section_contents += ReportList(objects, is_ordered = is_ordered)._to_html()
        self.section_contents += ['\t' + end + '\n']

    def add_link(self, link_url, link_name, end='<br>'):
        assert isinstance(end,str), 'end should be a str but is {}'.format(type(end))

        self.section_contents += ReportLink(link_url, link_name = link_name)._to_html()
        self.section_contents += ['\t' + end + '\n']

    def add_text(self, text, font_size=16, alignment='left', end='<br>'):
        assert isinstance(end,str), 'end should be a str but is {}'.format(type(end))

        self.section_contents += ReportText(text, font_size=font_size, alignment=alignment)._to_html()
        self.section_contents += ['\t' + end + '\n']

    def add_brakes(self, number_of_brakes):

        self.section_contents += ['\t' + '<br>'*number_of_brakes]

    def add_images(self, images, scales=1, embed=True, captions=None, end='<br><br>'):

        ''' images: could either be the path of an image, matplotlib figure (or a list)
        of these if you want to put multiple images side by side. By default, the images
        dont scale with browser size, this is a feature and not a bug (it does scale with
        the zoom setting of the browser though).

        scales: determines the scale of the width and height with respect to the original
        figure.

        embed: If true, the image is embedded in the html as a byte object and you do not
        need the original figure to view it in the report.

        captions: either a single str object or a list of strings which is the caption
        of each figure.
        '''

        widths = []
        div_widths = []
        heights = []

        if captions is None:
            captions = ['']*len(images)
        if not isinstance(images, list):
            images = [images]
        if not isinstance(captions, list):
            captions = [captions]
        if not isinstance(scales, list):
            assert isinstance(scales, (float,int)),'scales should be list, integer or float but is {}'.format(type(scales))
            scales = [scales]*len(images)

        assert len(captions) == len(images), 'captions and images list should have the same number of elements'
        assert len(scales) == len(images), 'scales and images list should have the same number of elements'
        assert isinstance(end,str), 'end should be a str but is {}'.format(type(end))

        try:
            font = ImageFont.truetype('arial.ttf', 16)
        except:
            font = ImageFont.truetype(module_path + '/fonts/arial.ttf', 16)

        for ind,image in enumerate(images):
            if isinstance(image,str):
                pimage = Image.open(image)
                image_width, image_height = pimage.size
                widths.append(int(scales[ind] * image_width))
                font_size = font.getsize(captions[ind])
                div_widths.append(max([int(scales[ind] * image_width), 1.01*font_size[0]]))
                heights.append(int(scales[ind] * image_height))
                pimage.close()

            elif isinstance(image, matplotlib.figure.Figure):
                image_width, image_height = image.get_size_inches()*image.dpi
                widths.append(int(scales[ind] * image_width))
                font_size = font.getsize(captions[ind])
                div_widths.append(max([int(scales[ind] * image_width), 1.01*font_size[0]]))
                heights.append(int(scales[ind] * image_height))
            else:
                raise ValueError('Images should be either in str format or matplotlib figure format but is {} instead'.format(type(image)))

        self.section_contents += ['\t<div style="width:' + str(int(sum(div_widths) + len(images)*10)) + 'px"n>\n']

        for ind,image in enumerate(images):

            if len(images)>1 and ind==len(images)-1:
                alignment='right'
            elif len(images)>1 and ind==len(images)-2:
                alignment='beforeright'
            elif len(images)==1:
                alignment='right'
            else:
                alignment='left'

            self.section_contents += ['\t' + x for x in ReportImage(image, widths[ind], heights[ind], alignment=alignment, caption=captions[ind])._to_html()]

        self.section_contents += ['\t</div>\n']
        self.section_contents += [end + '\n']



    def add_multitab(self, number_of_tabs, tab_titles, tab_contents):


        assert number_of_tabs == len(tab_titles), 'Number of tab titles should equal number of tabs'
        assert isinstance(tab_contents, list), 'tab_contents should be a list but is {} instead'.format(type(tab_contents))
        assert isinstance(tab_titles, list), 'tab_titles should be a list but is {} instead'.format(type(tab_titles))

        self.section_contents += ['\t<div class="tab">']

        for i in range(number_of_tabs):
            self.section_contents += ['\t\t<button class="tablinks" onclick="open_tabs(event, \'Tab%d\')">%s</button>'%(self.number_of_mtabs + i, tab_titles[i])]

        self.section_contents += ['\t</div>\n']

        for i in range(number_of_tabs):
            self.section_contents += ['\t<div id="Tab%d" class="tabcontent">'%(self.number_of_mtabs + i)]
            self.section_contents += ['\t<span onclick="this.parentElement.style.display="none"" class="topright">&times</span>']
            self.section_contents += ['\t<h3>%s</h3>'%tab_titles[i]]
            for content in tab_contents[i]:
                self.section_contents += ['\t' + x for x in content._to_html()]

            self.section_contents += ['\t</div>\n']
            self.section_contents += ['\n']

        self.number_of_mtabs += number_of_tabs

    def _write_section_html(self):

        self.html = ''

        if self.is_subsection:
            number_of_tabs = 5
        else:
            number_of_tabs = 4

        if self.is_subsection:
            self.section_contents.append('<hr class='+self.hr_style+'>  <!--END OF ' + self.name + '-->\n\n')

        for line in self.section_contents:
            self.html += '\t'*number_of_tabs + line + '\n'

class Report:

    '''A report object. It contains sections and page contents. write_html
    function converts each section to a page content and writes the page
    contents to a html file. After a section or subsection is created as an
    independent object it can be added by add_section function of this class.
    sections and subsections should be added in order of appearance. See the
    example_report.py in the examples section.

    Title can be added by add_report_title function after the object is created.

    pretext: can be added by add_report_pretext. This is something that is added
    before the title (could be such as links to homepage, or other related directories).

    containts_tex: If there will be tex formulas in the report then
    containts_tex should be set to True. tex rendering also requires internet
    connection (you can render as an html and print to pdf to have the tex
    formulas permanently). Tex formulas should be encased between {$ and $}. If tex
    formulas dont render in html, either there is no interenet connection
    or there is a wrong formula (try compiling the formulas in a tex editor
    to debug it). Note that when writing tex formulas, you need to escape
    special characters of python, for instance you need to write \\rightarrow
    instead of \rightarrow. This tex capability is intended for short demonstrations
    not proving long theorems. For longer tex documents you should prefer a proper
    tex editor.

    styles_path and scripts_path are the paths to the html styles and scripts
    included in the module. They can be modified as long as they conform with
    html otherwise might end up with unpredictable results (anything from the
    page not rendering to no visible effect)'''



    def __init__(self, styles_path=module_path + '/styles.py', scripts_path=module_path + '/scripts.py',
                 contains_tex = False):

        assert os.path.isfile(styles_path), 'Styles file {} does not exist.'.format(styles_path)
        assert os.path.isfile(scripts_path), 'Scripts file {} does not exist.'.format(scripts_path)
        assert isinstance(contains_tex,bool), 'contains_tex should be bool but is {} instead'.format(contains_tex)

        self.contains_tex = contains_tex

        try:
            styles_name = styles_path.split('/')[-1].split('.')[0]
        except:
            styles_name = styles_name

        try:
            scripts_name = scripts_path.split('/')[-1].split('.')[0]
        except:
            scripts_name = scripts_path

        self.style = importlib.import_module(styles_name, styles_path)
        self.scripts = importlib.import_module(scripts_name, scripts_path)

        assert 'hr_style' in dir(self.style), 'hr_style should be in style script'
        assert 'body_style' in dir(self.style), 'body_style should be in style script'
        assert 'fig_style' in dir(self.style), 'fig_style should be in style script'
        assert 'fig_caption_style' in dir(self.style), 'fig_caption_style should be in style script'

        self.page_contents = []
        self.open_tags = []
        self.page_title = []
        self.sections = []
        self.tab_ids = []
        self.html = ''
        self.pretext = ''
        self.number_of_sections = 0
        self.number_of_mtabs = 0

        self.page_contents.append('<!DOCTYPE html>')
        self.page_contents.append('<html>')
        self.page_contents.append('\t<body>')

        self.open_tags.append('</html>')
        self.open_tags.append('\t</body>')

    def add_report_title(self, title_text, color = "black"):

        assert isinstance(title_text,str),'Title text should be a str'

        self.page_title = ['\t\t<hr class="suphr"><!--START OF REPORT-->','\t\t<h1 style = "color: {}; text-align: center">{}</h1>'.format(color, title_text)]

        self.page_contents = self.page_contents[0:4] + self.page_title + self.page_contents[4:]

    def add_report_pretext(self, pretext):

        self.pretext = pretext

    def _write_section(self,section):
        section._write_section_html()
        self.html += '\n'

        self.html += section.html

    def write_html(self, output_path):

        if self.number_of_mtabs>0:
            assert 'tab_style' in dir(self.style), 'There are tabs in report but no tab style in style script'

        #add head with styles
        style_html = ['\t<head>', '\t\t<meta name="viewport" content="width=device-width, initial-scale=1">','\t\t<style>']

        style_html += [self.style.body_style  , self.style.hr_style, self.style.fig_style, self.style.fig_caption_style]

        if self.number_of_mtabs > 0:
            style_html += [self.style.tab_style]

        style_html += ['\t\t</style>']

        #add scripts
        scripts_html = []
        if self.number_of_mtabs > 0:
            assert 'tab_script' in dir(self.scripts), 'There are tabs in the report but no tabs script in scripts file'
            scripts_html +=  [self.scripts.tab_script]

        if self.contains_tex:
            assert 'tex_script' in dir(self.scripts), 'There are tex formukas in the report but no tex script in scripts file'
            scripts_html += [self.scripts.tex_script]

        #add style and scripts to the contents
        self.page_contents = self.page_contents[0:1] + style_html + scripts_html + ['\t</head>\n'] + [self.pretext] + self.page_contents[2:]

        for line in self.page_contents:
            self.html += line + '\n'

        for section in self.sections:
            self._write_section(section)

        self.html += '\t\t<hr class="suphr">  <!--END OF REPORT-->\n\n'

        for tag in self.open_tags[::-1]:
            self.html += tag + '\n'

        file = open(output_path,'w')
        file.writelines(self.html)

    def add_section(self, section):
        self.number_of_sections += 1
        self.number_of_mtabs += section.number_of_mtabs
        self.sections.append(section)
