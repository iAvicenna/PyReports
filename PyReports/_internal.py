#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 18:51:06 2022

@author: Sina Tureli
"""

import PIL as _PIL
import _io 
import re as _re
import matplotlib.pyplot as _plt
import base64 as _b64
from bs4 import BeautifulSoup as _bs

def fig2img(fig: _plt.Figure):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    buf = _io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = _PIL.Image.open(buf)
    return img


def image_to_byte_array(image:_PIL.Image):
    """Convert an Image to byte like array without saving to disk"""
    imgByteArr = _io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def file_to_base64(filepath:str):
    """
    Returns the content of a file as a Base64 encoded string.
    :param filepath: Path to the file.
    :type filepath: str
    :return: The file content, Base64 encoded.
    :rtype: str
    """
    with open(filepath, 'rb') as f:
        encoded_str = _b64.b64encode(f.read())
    return encoded_str


def html_tokenizer(html:str):
    
    html_soup = _bs(html, 'html.parser')
    
    head_html = str(html_soup.head)
    body_html = str(html_soup.body)
    html_tokens = {}
    if head_html:
        html_tokens['head'] = []
        
        head_soup = _bs(head_html, 'html.parser')
        
        for tag in ['script','link','style', 'div']:
            html_tokens['head']+= [str(elem) for elem in head_soup.find_all(tag)]

    html_tokens['body'] = body_html
            
    return html_tokens

    
def replace_leading_spaces(source, char="&nbsp;"):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped


def format_text(text, parent_depth, leading_space="&nbsp;", is_code=False,
                formatted=False):
            
    if len(text)>0 and text[0]=='\n':
        text = text[1:]
    if len(text)>0 and text[-1]=='\n':
        text = text[:-1]
        
    if not is_code:
        fixed_indel = 2
        if not formatted:
            end_char = ''
            line_char = '<br><br>'
        else:
            end_char = '<br>'
            line_char = ''
    else:
        fixed_indel = 0  
        end_char = '<br>'
        line_char = ''

    text_split = split_by_text_newspace(text)
    indel_lengths = [len(text_part)-len(text_part.lstrip()) for text_part
                 in text_split if not all(x in ' ' for x in text_part) and text_part != '']
    
    if len(indel_lengths)==0:
        min_indel = 0
    else:
        min_indel = min(indel_lengths)
                
    text_split = [part[min_indel:] if any(x not in ['',' '] for x in part[min_indel:])
                  else '' for part in text_split]
    text_split = [replace_leading_spaces(part, char=leading_space) 
                  for part in text_split]
    text_split = [part + '<br>' if _is_item(part) else part for
                  part in text_split]

    if all(x == ' ' for x in text_split[-1]):
        text_split = text_split[:-1]
        
    total_indel = '    '*(parent_depth + fixed_indel)
    
    text = '\n'.join([total_indel + x + f'{line_char}' if x=='' or all(y == ' ' for y in x)
                      else total_indel + x + f'{end_char}' for x in text_split])

    return text


def split_by_text_newspace(text):
    '''
    split text by newspace which are not inside quotes. 
    '''
    
    open_quotes = []
    new_space_positions = [-1]
    new_text = text
    offset = 0
    
    for pos,let in enumerate(text):
        if let == '"':
            if len(open_quotes)>0 and  open_quotes[-1] == '"':
                open_quotes.pop()
            else:
                open_quotes.append('"')
            
        if let == '\n' and len(open_quotes)==0:
            new_space_positions.append(pos-offset)
        elif let == '\n' and len(open_quotes)>0:
            new_text = text[:pos] + '' + text[pos+1:]
            offset += 1
    
    text = new_text
    new_space_positions.append(len(text))
    
    split_text = []
    counter = 0
    
    for ind_pair,(pos1,pos2) in enumerate(zip(new_space_positions[0:-1], new_space_positions[1:])):
        pos1 -= counter
        pos2 -= counter
        
        text_part = text[pos1+1:pos2]
        text = text[pos2+1:]
        
        counter += pos2+1

        split_text.append(text_part)
        
    return split_text
        
        
def _is_item(part):
    
    if len(part)==0:
        return False
    elif part[0]=='-':
        return True
    elif _re.search('^\d+(.|-)',part) is not None:
        return True
    else: return False
    
    
        
        
    
    