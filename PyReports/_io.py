#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 17:08:51 2022

@author: Sina Tureli
"""

import inspect as _gadget
import json as _js
import pydoc as _pyd
import os as _os

import PyReports as pr

_MODULE_PATH = _os.path.dirname(_os.path.realpath(__file__))

_FORMATTERS={
    'none': {
        'bolden':lambda x: x,
        'tag':['','']
        },
    
   'terminal': {
        'bolden':lambda x:'\033[1m' + x + '\033[0m',
        'tag':['','']
        },
    
    'html': {
        'bolden':lambda x: '<strong>' + x + '</strong>',
        'tag':['<pre>\n','</pre>\n']
        },
    
    }


def create_template(template_name, pretext, section_titles=None):
    
    report = pr.Report('')
    report.pretext(pretext)
    
    if section_titles is not None:
        with report:
            for section_title in section_titles:
                
                pr.Section(section_title)
            
    if template_name[-5:]!='.json':
        template_name += '.json'
        
    report.to_json(f'{_MODULE_PATH}/templates/{template_name}')
    
    return report
            

def from_template(template_name, report_title):
    
    if template_name[-5:]!='.json':
        template_name += '.json'
    
    report = from_json(f'{_MODULE_PATH}/templates/{template_name}')
    
    report.title(report_title)
    
    return report

def from_json(jdict_path=None, _jdict=None, _parent=None):
    
    '''
    Allows reading jdict files created by the to_json function above.
    Normally intended to be called on the json created by a report object
    though in principle could be called on a json created by any _Node inherited
    object.
    
    The user is expected to call it via supplying the jdict_path where as _jdict 
    and _parent is used internally.
    '''
    pr.objects._Context._loading_from_json = True
    
    if _jdict is None and jdict_path is None:
        raise ValueError('You must provide one of jdict_path (takes precendence) or jdict')
        
    if jdict_path is None and _jdict is not None:
        assert isinstance(_jdict,dict), 'jdict must be a dict'
    
    if jdict_path is not None:
        with open(jdict_path,'r') as fp:
            _jdict = _js.loads(''.join(fp.readlines()))
        
    assert 'type' in _jdict, 'pyreport json files must contain a type field'
        
    obj_type = _pyd.locate(_jdict['type'])  # get the object class
    
    if obj_type is None:
        obj_type = _jdict['type']
        raise ValueError(f'Could not find object of type {obj_type}')
    
    init_argspec = [x for x in _gadget.getfullargspec(obj_type.__init__)[0] #  get all arguments required for init 
               if x not in ['self']]                                        #  except self
    
    
    init_args = {x:_jdict['_'+x] for x in init_argspec if x!='parent'}  # get the values for these arguments which will be stored
                                                                        # in the dict, except the parent which should be either None
                                                                        # if the function is called by the user else initialized internally
    if 'parent' in init_argspec:
        init_args['parent'] = _parent                                   # if a parent is supplied to from_json call during addition of childs
                                                                        # it will be included here in the init args
    
    node = obj_type(**init_args)  #  initiate the object
    
    for attr in _jdict:
        if attr not in ['type','_is_root','_depth','_has_tabs',         # set attrs which may have been changed after initialization
                        '_has_grid','_children']:                       # note: child parent relations might change so they will be 
                                                                        # taken care of automatically when children are created in this 
                        
                        
                        
            node.__setattr__(attr, _jdict[attr])
        
    
    for child in _jdict['_children']:           # now recursively do the same for every child of this object
        from_json(_jdict=child, _parent=node)   # required info for the children will be in the children field
                                                # of the json. Calling this will automatically sort the parent
                                                # child relations via object initiation. Grids, Folds and Tabs 
                                                # automatically create their children images during the obj 
                                                # initialization above so no need to do it for them. This is 
                                                # meant for sections really.

    pr.objects._Context._loading_from_json = False

    return node


def to_json(node, path):
    
    '''
    Given a node, saves its information as a json file 
    to path.
    '''
    
    assert isinstance(node,pr.objects._Node),f'node should be a _Node but was {type(node)}'
    
    jdict = _to_dict(node)
    
    json_str = _js.dumps(jdict, indent=4)
    
    with open(path,'w') as fp:
        
        fp.writelines(json_str)
    
    
def to_ascii(node, detailed=True, print_address=False,  _depth=None, 
             _print_root=None, formatting='terminal', link_to_sections=False):
    
    formatter = _FORMATTERS[formatting]
    tag0 = formatter['tag'][0]
    tag1 = formatter['tag'][1]
    
    if _depth is None:
        _depth = 0 
        
    indent = ''
    if _print_root is None:
        _print_root = node
        
    if detailed:
        section_only=False
    else:
        section_only=True
        
        
    if isinstance(node,(pr.containers.Report, pr.containers.Section)) or detailed: 

        node_type = str(type(node))[8:-2].split('.')[-1].upper()
        
        if node_type == 'SECTION':
            if node._is_subsection:
                node_type = formatter['bolden']('SUBSECTION') 
            else:
                node_type = formatter['bolden'](node_type) 
        elif node_type =='REPORT':
            node_type = formatter['bolden'](node_type)
           
        ancestors = node._ancestors(until=_print_root)
     
        if node != node._root(until=_print_root)._descendants(section_only=section_only)[-1]:
            for ind in range(len(ancestors)-2):
                if ( (detailed and ancestors[ind]._children[-1] != ancestors[ind+1])
                    or (not detailed and len(ancestors[ind].sections)!=0 and ancestors[ind].sections[-1] != ancestors[ind+1])
                    ):
                    indent += '│   '
                else:
                    indent += '    '
        else:
            indent += '    '*(_depth-1)
                
        if (node._parent is None
            or (not detailed and (len(node._parent.sections)==0 or node != node._parent.sections[-1]))
            or (detailed and (len(node._parent._children)==0 or node != node._parent._children[-1]))
            ):
            indent += '├───'*int(_depth>0) 
        else:
            indent += '└───'*int(_depth>0) 
        
            
        node_str = hex(id(node))*print_address + ' ' + indent + f'{node_type}' 
        
        if isinstance(node, (pr.containers.Section,pr.containers.Report)):

            if isinstance(node, pr.containers.Section) and link_to_sections:
                title = f'<a href="#S{node._section_no_str}">{node._title}</a>'
            else:
                title = node._title
            
            node_str += f' ({title})'*(not print_address) 
            
        if _depth==0:
            node_str = tag0 + node_str + '\n'
        else:
            node_str += '\n'
        
                
        if len(node._children)==0:

            return node_str + tag1*int(_depth==0)
        else:
            for child in node._children:
                node_str += to_ascii(child, detailed=detailed, print_address=print_address,
                                     _depth = _depth+1, _print_root=_print_root, 
                                     formatting=formatting, 
                                     link_to_sections=link_to_sections)
        
            return node_str + tag1*int(_depth==0)
                
    else:
       return tag0*int(_depth==0) + '' + tag1*int(_depth==0)
   
    
def _to_dict(node):
    
    '''
    convert relevant information in a node to dict so that it can be
    saved as a json
    '''

    assert isinstance(node,pr.objects._Node),f'node should be a _Node but was {type(node)}'

    keys = [x for x in node.__dict__.keys()
               if x not in ['_parent']]
    
    node_dict = {}
    
    node_dict['type'] = str(type(node))[8:-2]   # needs to be saved as str for JSON serializability
    for key in keys: node_dict[key]=node.__getattribute__(key) 
    
    node_dict['_children'] = []
    
    for child in node._children:
        node_dict['_children'].append(_to_dict(child))
    
    return node_dict
       
    