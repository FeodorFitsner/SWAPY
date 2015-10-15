# unit tests for codegenerator
# Copyright (C) 2015 Matiychuk D.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

from contextlib import contextmanager
import os
import string
import unittest

import proxy
import code_manager
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python


def get_proxy_object(pwa_window, path):
    if not pwa_window:
        proxy_object = proxy.PC_system(None)
    else:
        proxy_object = proxy.Pwa_window(pwa_window)
    for target_sub in path:
        for name, pwa_object in proxy_object.Get_subitems():
            if target_sub in name:
                proxy_object = pwa_object
                break

    return proxy_object


@contextmanager
def test_app(filename):
    mfc_samples_folder = os.path.join(os.path.dirname(__file__),
                                      r"..\apps\MFC_samples")
    if is_x64_Python():
        sample_exe = os.path.join(mfc_samples_folder,
                                  "x64",
                                  filename)
    else:
        sample_exe = os.path.join(mfc_samples_folder, filename)
    app = Application().start(sample_exe)
    yield app
    app.kill_()


class CodeGeneratorTestCases(unittest.TestCase):

    def setUp(self):

        """
        Since the tests require different apps, use `with` statement instead.
        All setUp actions moved in the test_app contextmanager.
        """

        pass

    def tearDown(self):

        """
        All app's tearDown moved into the test_app contextmanager.
        """

        code_manager.CodeManager().clear()  # Clear single tone CodeManager
        reload(code_manager)  # Reset class's counters
        reload(proxy)  # Reset class's counters

    def testComboBoxCode(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Connect(title=u'Common " \
            "Controls Sample', class_name='#32770')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "combobox1 = pwa_window1.ComboBox\n" \
            "combobox1.Select('Gray')\n\n"

        path = (u'Common Controls Sample',

                u'Gray, Gray, White, Black',

                u'Gray',
                )

        with test_app("CmnCtrl3.exe"):
            proxy_app = get_proxy_object(None, path)
            code = proxy_app.Get_code('Select')

        self.assertEquals(expected_code, code)

    def testSysListView32Code(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "{app_ident}1 = Application().Connect(title=u'RowList Sample " \
            "Application', class_name='{class_name}')\n" \
            "{win_ident}1 = {app_ident}1['RowList Sample Application']\n" \
            "syslistview1 = {win_ident}1['1']\n" \
            "syslistview1.Click()\n\n"

        path = (u'RowList Sample Application',

                u'Yellow, 255, 255, 0, 40, 240, 120, Neutral, Red, 255, 0, 0, '
                u'0, 240, 120, Warm, Green, 0, 255, 0, 80, 240, 120, Cool, '
                u'Magenta, 255, 0, 255, 200, 240, 120, Warm, Cyan, 0, 255, '
                u'255, 120, 240, 120, Cool, Blue, 0, 0, 255, 160, 240, 120, '
                u'Cool, Gray, 192, 192, 192, 160, 0, 181, Neutral',

                u'Line',
                )

        with test_app("RowList.exe"):
            window = Application().Connect(
                title=u'RowList Sample Application')[
                'RowList Sample Application']

            class_name = window.GetProperties()['Class']
            crtl_class = filter(lambda c: c in string.ascii_letters,
                                class_name).lower()

            proxy_app = get_proxy_object(None, path)
            code = proxy_app.Get_code('Click')

        expected_code = expected_code.format(app_ident="app_%s" % crtl_class,
                                             win_ident=crtl_class,
                                             class_name=class_name)
        self.assertEquals(expected_code, code)

    def testSysTabControl32Code(self):
        expected_code = \
            "f<bug>rom pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Connect(title=u'Common " \
            "Controls Sample', class_name='#32770')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "systabcontrol1 = pwa_window1.TabControl\n" \
            "systabcontrol1.Select('CTreeCtrl')\n\n"

        path = (u'Common Controls Sample',

                u'CTreeCtrl, CAnimateCtrl, CToolBarCtrl, CDateTimeCtrl, '
                u'CMonthCalCtrl',

                u'CTreeCtrl',
                )

        with test_app("CmnCtrl1.exe"):
            proxy_app = get_proxy_object(None, path)
            code = proxy_app.Get_code('Select')

        self.assertEquals(expected_code, code)

    def testToolbarWindow32Code(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Connect(title=u'Common " \
            "Controls Sample', class_name='#32770')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "toolbarwindow1 = pwa_window1.Toolbar2\n" \
            "pwa_toolbar_button1 = toolbarwindow1.Button('Line')\n" \
            "pwa_toolbar_button1.Click()\n\n"

        path = (u'Common Controls Sample',

                u'Erase, Pencil, Select, Brush, Airbrush, Fill, Line, Select '
                u'Color, Magnify, Rectangle, Round Rect, Ellipse',

                u'Line',
                )

        with test_app("CmnCtrl1.exe") as app:
            app.Dialog.TabControl.Select('CToolBarCtrl')  # open needed tab
            proxy_app = get_proxy_object(None, path)
            code = proxy_app.Get_code('Click')

        self.assertEquals(expected_code, code)
