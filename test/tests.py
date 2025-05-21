#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  7 19:22:59 2022

@author: Sina Tureli
"""

import unittest
import PyReports as pr
import os
import sys
cdir = os.path.dirname(__file__)
examples_folder = os.path.join(cdir, 'examples')
sys.path.insert(1,  examples_folder)

class TestExampleReports(unittest.TestCase):

    '''
    Run the example_report in examples section
    '''
    def setUp(self):
        examples_folder = os.path.join(cdir, 'examples')
        sys.path.insert(1,  examples_folder)

    def test_run1(self):
        self.setUp()
        import example_report


class TestParenting(unittest.TestCase):


    def test_section_parent_change(self):

        with pr.Report('Test1') as report1:
            with pr.Section('Section1') as section1:
                pr.Txt('Lorem Ipsum')

        report2 = pr.Report('Test2')
        section1._parent = report2

        self.assertTrue(section1 in report2.sections)
        self.assertTrue(section1 not in report1.sections)
        self.assertTrue(section1._parent == report2)
        self.assertTrue(section1._parent != report1)


    def test_subsection_parent_change(self):

        with pr.Report('Test1'):
            with pr.Section('Section1') as section1:
                with pr.Section('Subsection1') as subsection1:
                    pr.Txt('Lorem Ipsum')


        with pr.Report('Test2') as report2:
            section2 = pr.Section('Section1', parent=report2)

        subsection1._parent = section2

        self.assertTrue(subsection1 in section2.sections)
        self.assertTrue(subsection1 not in section1.sections)
        self.assertTrue(subsection1._parent == section2)
        self.assertTrue(subsection1._parent != section1)


    def test_subsection_parent_change_nested(self):

        with pr.Report('Test1') as report1:
            with pr.Section('Section1'):
                with pr.Section('Subsection1'):
                    pr.Txt('Lorem Ipsum')

                with pr.Section('Subsection2') as subsection2:
                    pr.Txt('Lorem Ipsum')

                with pr.Section('Subsection3'):
                    pr.Txt('Lorem Ipsum')

            with pr.Section('Section1'):

                with pr.Section('Subsection4'):
                    pr.Txt('Lorem Ipsum')


        self.assertTrue(str(report1)==
                        ' \x1b[1mREPORT\x1b[0m (Test1)\n ├───\x1b[1mSECTION\x1b[0m (Section1)\n │   ├───\x1b[1mSUBSECTION\x1b[0m (Subsection1)\n │   │   └───TEXT\n │   ├───\x1b[1mSUBSECTION\x1b[0m (Subsection2)\n │   │   └───TEXT\n │   └───\x1b[1mSUBSECTION\x1b[0m (Subsection3)\n │       └───TEXT\n └───\x1b[1mSECTION\x1b[0m (Section1)\n     └───\x1b[1mSUBSECTION\x1b[0m (Subsection4)\n         └───TEXT\n')

        with pr.Report('Test2') as report2:
            section3 = pr.Section('Section1', parent=report2)

        subsection2._parent = section3

        self.assertTrue(str(report1)==
                        ' \x1b[1mREPORT\x1b[0m (Test1)\n ├───\x1b[1mSECTION\x1b[0m (Section1)\n │   ├───\x1b[1mSUBSECTION\x1b[0m (Subsection1)\n │   │   └───TEXT\n │   └───\x1b[1mSUBSECTION\x1b[0m (Subsection3)\n │       └───TEXT\n └───\x1b[1mSECTION\x1b[0m (Section1)\n     └───\x1b[1mSUBSECTION\x1b[0m (Subsection4)\n         └───TEXT\n'
                        )
        self.assertTrue(str(report2)==
                        ' \x1b[1mREPORT\x1b[0m (Test2)\n └───\x1b[1mSECTION\x1b[0m (Section1)\n     └───\x1b[1mSUBSECTION\x1b[0m (Subsection2)\n         └───TEXT\n'
                        )


    def test_object_parent_change(self):

        with pr.Report('Test1'):
            with pr.Section('Section1'):
                with pr.Section('Subsection1') as subsection1:
                    text = pr.Txt('Lorem Ipsum')

        with pr.Report('Test2') as report2:
            section2 = pr.Section('Section1', parent=report2)

        text._parent = section2

        self.assertTrue(text in section2._children)
        self.assertTrue(text not in subsection1._children)
        self.assertTrue(text._parent == section2)
        self.assertTrue(text._parent != subsection1)


    def test_parent_child_relation_checker(self):

        with pr.Report('Test1') as report1:
            with pr.Section('Section1') as section1:
                pr.Txt('Lorem Ipsum')

        report2 = pr.Report('Test2')
        section1._parent = report2

        self.assertTrue(section1 in report2.sections)
        self.assertTrue(section1 not in report1.sections)
        self.assertTrue(section1._parent == report2)
        self.assertTrue(section1._parent != report1)


if __name__ == '__main__':
    unittest.main()
