#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 15:07:58 2020

@author: avicenna
"""


other_styles = '''''' #add any extra styles here

body_style = '''
            body {font-family: Courier New; font-size:16px}'''

p_style = '''
            p {
              white-space: pre;
             }'''

fig_caption_style = '''
            figcaption {font-size:16px; word-wrap:break-word}
            '''

hr_style = '''
            hr.suphr {height:20px;width:200%;text-align:left;margin-left:0;color:gray;background-color:gray}

            hr.subhr {height:5px;width:200%;text-align:left;margin-left:0;color:gray;background-color:gray}'''

fig_style = '''
            figure.left {
              margin-top: 0px;
              margin-bottom: 0px;
              margin-right: 0px;
              margin-left: 0px;
              padding: 5px;
              float: left;
            }

            figure.beforeright{
              margin-top: 0px;
              margin-bottom: 0px;
              margin-right: 5px;
              margin-left: 0px;
              padding: 5px;
              float: left;
            }

            figure.right {
              margin-top: 0px;
              margin-bottom: 0px;
              margin-right: 0px;
              margin-left: 0px;
              padding: 5px;
              float: none;
            }

'''

tab_style = '''
            .tab {
              overflow: hidden;
              border: 1px solid #ccc;
              background-color: #f1f1f1;
            }

            /* Style the buttons inside the tab */
            .tab button {
              background-color: inherit;
              float: left;
              border: none;
              outline: none;
              cursor: pointer;
              padding: 14px 16px;
              transition: 0.3s;
              font-size: 17px;
            }

            /* Change background color of buttons on hover */
            .tab button:hover {
              background-color: #ddd;
            }

            /* Create an active/current tablink class */
            .tab button.active {
              background-color: #ccc;
            }

            /* Style the tab content */
            .tabcontent {
              display: none;
              padding: 6px 12px;
              border: 1px solid #ccc;
              border-top: none;
            }

            /* Style the close button */
            .topright {
              float: right;
              cursor: pointer;
              font-size: 28px;
            }

            .topright:hover {color: red;}'''