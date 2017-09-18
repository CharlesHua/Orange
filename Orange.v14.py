#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Data dispaly and curve fit

@author: Jiannan Hua
last edited: Sept.1  2017
"""

import sys

import numpy as np
from PyQt4 import QtCore, QtGui
#from numpy import loadtxt
#from matplotlib.backends import qt_compat
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from lmfit.models import ConstantModel, LinearModel, QuadraticModel, LorentzianModel, GaussianModel, Model
from lmfit.parameter import Parameters

import UserDefinedFunction

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_tight_layout({'h_pad'})
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    #    FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
    #    FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
       # print 'initial_figure'
        x = np.random.randn(20)
        z = np.random.randn(20)
        self.axes.scatter(x, z)


class ApplicationWindow(QtGui.QMainWindow):
    """docstring for ApplicationWindow"""
    def __init__(self, arg):
        super(ApplicationWindow, self).__init__()
        self.arg = arg

        # def Init_Data():
        self.length = 0
        self.x = []
        self.y = []
        self.y_err = []
        self.y_errExist = False
        self.lineList = []
        self.repoter = ''

        # Init_Data()
        self.Init_Ui()


    def Init_Ui(self):

        '''statusBar and menuBar'''
        self.statusBar()
        menubar = self.menuBar()

        openFileAction = QtGui.QAction('Open File...', self)
        openFileAction.setShortcut('Ctrl+O')
        openFileAction.setStatusTip('Open New File')
        openFileAction.triggered.connect(self.OpenFile)

        clearFitAction = QtGui.QAction('Clear Fit', self)
        clearFitAction.setStatusTip('Clear Fit')
        clearFitAction.triggered.connect(self.ClearFit)

        linearFitAction = QtGui.QAction('Linear Fit', self)
        linearFitAction.setStatusTip('FitLinear: linear regression on XY data')
        linearFitAction.triggered.connect(
            lambda: self.Fitting(True, LinearModel()))

        quadraticFitAction = QtGui.QAction('Quadratic Fit', self)
        quadraticFitAction.setStatusTip(
            'FitQuadratic: quadratic regression on XY data')
        quadraticFitAction.triggered.connect(
            lambda: self.Fitting(True, QuadraticModel()))

        lorentzianFitAction = QtGui.QAction('Lorentzian Fit', self)
        lorentzianFitAction.setStatusTip(
            'FitLorentzian: Lorentzian regression on XY data')
        lorentzianFitAction.triggered.connect(
            lambda: self.Fitting(True, LorentzianModel()))

        lorentzianFitWithConstantBaseAction = QtGui.QAction(
            'Lorentzian Fit With Constant Base', self)
        lorentzianFitWithConstantBaseAction.setStatusTip(
            'FitLorentzianWithConstantBase: Lorentzian regression on XY data')
        lorentzianFitWithConstantBaseAction.triggered.connect(
            lambda: self.Fitting(True, LorentzianModel(), ConstantModel()))

        lorentzianFitWithLinearBaseAction = QtGui.QAction(
            'Lorentzian Fit With Linear Base', self)
        lorentzianFitWithLinearBaseAction.setStatusTip(
            'FitLorentzianWithLinearBase: Lorentzian regression on XY data')
        lorentzianFitWithLinearBaseAction.triggered.connect(
            lambda: self.Fitting(True, LorentzianModel(), LinearModel()))

        gaussianFitAction = QtGui.QAction('Gaussian Fit', self)
        gaussianFitAction.setStatusTip(
            'FitGaussian: Gaussian regression on XY data')
        gaussianFitAction.triggered.connect(
            lambda: self.Fitting(True, GaussianModel()))

        gaussianFitWithConstantBaseAction = QtGui.QAction(
            'Gaussian Fit With Constant Base', self)
        gaussianFitWithConstantBaseAction.setStatusTip(
            'FitGaussianWithConstantBase: Gaussian regression on XY data')
        gaussianFitWithConstantBaseAction.triggered.connect(
            lambda: self.Fitting(True, GaussianModel(), ConstantModel()))

        gaussianFitWithLinearBaseAction = QtGui.QAction(
            'Gaussian Fit With Linear Base', self)
        gaussianFitWithLinearBaseAction.setStatusTip(
            'FitGaussianWithLinearBase: Gaussian regression on XY data')
        gaussianFitWithLinearBaseAction.triggered.connect(
            lambda: self.Fitting(True, GaussianModel(), LinearModel()))

        userDefinedFitAction = QtGui.QAction('User Defined Function Fit', self)
        userDefinedFitAction.setStatusTip('User Defined Function regression on XY data')
        userDefinedFitAction.triggered.connect(self.UserDefinedFunctionFit)

        aboutOrangeAction = QtGui.QAction('About Orange', self)
        aboutOrangeAction.triggered.connect(self.about_orange)

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFileAction)

        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(clearFitAction)

        analysisMenu = menubar.addMenu('&Analysis')
        analysisMenu.addAction(linearFitAction)
        analysisMenu.addAction(quadraticFitAction)
        analysisMenu.addAction(lorentzianFitAction)
        analysisMenu.addAction(lorentzianFitWithConstantBaseAction)
        analysisMenu.addAction(lorentzianFitWithLinearBaseAction)
        analysisMenu.addAction(gaussianFitAction)
        analysisMenu.addAction(gaussianFitWithConstantBaseAction)
        analysisMenu.addAction(gaussianFitWithLinearBaseAction)
        analysisMenu.addAction(userDefinedFitAction)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(aboutOrangeAction)

        '''data table'''
        self.table = QtGui.QTableWidget()
        self.table.setRowCount(5)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['X', 'Y', 'Y_err'])


        # set data
        for col in range(3):
            newItem = QtGui.QTableWidgetItem('0')
            newItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.table.setItem(0, col, newItem)

        # tooltip text
        self.table.horizontalHeaderItem(0).setToolTip("Column 1")
        self.table.horizontalHeaderItem(1).setToolTip("Column 2")

        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setFrameShape(QtGui.QFrame.StyledPanel)


        # picture
        self.pictr = MyMplCanvas(width=5, height=4, dpi=100)
        self.pictr.axes.set_xlabel('X')
        self.pictr.axes.set_ylabel('Y')
        self.pictr.draw()

        self.pictrErr = MyMplCanvas(width=5, height=3, dpi=100)
        self.pictrErr.axes.set_xlabel('X')
        self.pictrErr.axes.set_ylabel('Y.data-Y.exp')
        self.pictrErr.draw()

        self.mplToolbar = NavigationToolbar(self.pictr, None)


        # text (report)
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setReadOnly(True)


        # splitter (assemble widgets)
        splitterV = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterV.addWidget(self.mplToolbar)
        splitterV.addWidget(self.pictr)
        splitterV.addWidget(self.pictrErr)
        splitterV.setStretchFactor(1, 5)
        splitterV.setStretchFactor(2, 4)

        splitterH = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitterH.addWidget(self.table)
        splitterH.addWidget(splitterV)
        splitterH.addWidget(self.textEdit)
        # splitterH.setStretchFactor(0, 0)
        # splitterH.setStretchFactor(1, 0)
        # splitterH.setStretchFactor(2, 0)

        self.setCentralWidget(splitterH)
        self.setGeometry(200, 100, 800, 600)
        self.setWindowTitle('Orange')

        self.show()


    def DrawDataPoint(self):
        self.pictr.axes.cla()
        self.pictr.axes.set_xbound(min(self.x), max(self.x))
        self.pictr.axes.set_ybound(min(self.y), max(self.y))
        self.pictr.axes.scatter(self.x, self.y, c='k')
        if self.y_errExist:
            self.pictr.axes.errorbar(self.x, self.y, yerr=self.y_err, fmt='none')
        self.pictr.axes.set_xlabel('X')
        self.pictr.axes.set_ylabel('Y')
        self.pictr.draw()

        self.lineList = []

        self.pictrErr.axes.cla()
        self.pictrErr.axes.set_xbound(self.pictr.axes.get_xbound())
        self.pictrErr.axes.set_xlabel('X')
        self.pictrErr.axes.set_ylabel('Y.data-Y.exp')
        self.pictrErr.draw()

        self.repoter = ''
        self.textEdit.setText(self.repoter)


    def OpenFile(self):
        def ImportData():
            data = np.loadtxt(address_str)
           # print data
            self.x = data[:, 0]
            self.y = data[:, 1]
            try:
                self.y_err = data[:, 2]
                self.y_errExist = True
            except IndexError:
                self.y_errExist = False
                # self.y_err = 0

            # another way to import data
            # self.x = []
            # self.y = []
            # for line in file:
            #     x_i, y_i = line.split()
            #     self.x.append(float(x_i))
            #     self.y.append(float(y_i))

        def DisplayInTable():
            self.table.setRowCount(len(self.x))
            self.length = len(self.x)
            for i in range(self.length):
                # Align left
                # self.table.setItem(i,0, QtGui.QTableWidgetItem(str(self.x[i])))
                # self.table.setItem(i,1, QtGui.QTableWidgetItem(str(self.y[i])))
                # Align right
                newItem = QtGui.QTableWidgetItem(str(self.x[i]))
                newItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.table.setItem(i, 0, newItem)
                newItem = QtGui.QTableWidgetItem(str(self.y[i]))
                newItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.table.setItem(i, 1, newItem)
                if self.y_errExist:
                    newItem = QtGui.QTableWidgetItem(str(self.y_err[i]))
                else:
                    newItem = QtGui.QTableWidgetItem('')
                newItem.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.table.setItem(i, 2, newItem)

        fileAddress = QtGui.QFileDialog.getOpenFileName(self, 'Open file', directory='')
        # print 'fileAddress: ', fileAddress
        address_str = str(fileAddress)
        # print 'address_str: ', address_str
        f = open(fileAddress, 'r')
        # print type(f)
        # print 'f: ', f
        with f:
            ImportData()
            DisplayInTable()
            self.DrawDataPoint()
            self.setStatusTip(fileAddress)


    def ClearFit(self):
        # empty is False
        if len(self.x):
            self.DrawDataPoint()


    def DisplayResult(self, out):
        xwide = np.linspace(min(self.x), max(self.x), 501)
        y_predicted = out.eval(x=xwide)

        # draw a line and get its name
        newline, = self.pictr.axes.plot(xwide, y_predicted, label=str(out.model.name))
        self.lineList.append(newline)
        self.pictr.axes.legend(handles=self.lineList, loc=1)
        self.pictr.draw()

        # draw err picture
        self.pictrErr.axes.scatter(self.x, self.y - out.best_fit)
        self.pictrErr.axes.axhline(y=0, color='k', linestyle='--', linewidth=1.0)
        self.pictrErr.axes.set_xbound(self.pictr.axes.get_xbound())
        self.pictrErr.draw()

        # print fit repoter
        self.repoter += out.fit_report() + '\n'
        self.textEdit.setText(self.repoter)


    # def Fitting(self, mod):
    #     pars = mod.guess(self.y, x = self.x)
    #     out  = mod.fit(self.y, pars, x = self.x)
    #     self.DisplayResult(out)



    def Fitting(self, allow_guess=True, *modelList):

        mod = reduce(lambda x, y: x + y, modelList)

        if len(self.x) < len(mod.param_names):
            QtGui.QMessageBox.warning(
                self, 'Warning', 'Insufficient data points to make fit')
            return

        class ParaInputDialog(QtGui.QDialog):
            """docstring for ParaInputDialog"""
            def __init__(self, parent):
                super(ParaInputDialog, self).__init__()
                # self.arg = arg
                self.parent = parent
                self.pars = Parameters()
                # pars is a instance whose type is lmfit.parameter.Parameters
                # it inherits from dict
                self.Init_Ui()


            def Init_Ui(self):
                grid = QtGui.QGridLayout()
                grid.setSpacing(1)
                self.lableDict = {}
                self.lineEditDict = {}
                lab = QtGui.QLabel('Please input initial parameters')
                grid.addWidget(lab, 0, 0, 1, 2)
                # mod.param_names is a list
                for (j, para) in enumerate(mod.param_names):
                    self.lableDict[para] = QtGui.QLabel(para)
                    self.lineEditDict[para] = QtGui.QLineEdit()
                    grid.addWidget(self.lableDict[para], j+1, 0)
                    grid.addWidget(self.lineEditDict[para], j+1, 1)

                defaultButton = QtGui.QPushButton('Default')
                defaultButton.setToolTip('Use default predicted values')
                defaultButton.clicked.connect(self.defaultButtonClicked)

                okButton = QtGui.QPushButton('OK')
                okButton.clicked.connect(self.okButtonClicked)

                grid.addWidget(defaultButton)
                grid.addWidget(okButton)
                self.setLayout(grid)

                self.setWindowTitle("Input Predicted parameters")
                self.setWindowModality(QtCore.Qt.ApplicationModal)
                self.exec_()


            def defaultButtonClicked(self):
                if allow_guess:
                    self.pars = Parameters()
                    for model in modelList:
                        self.pars += model.guess(self.parent.y, x=self.parent.x)
                    for para in self.lineEditDict:
                        self.lineEditDict[para].setText(
                            str(self.pars[para].value.item()))
                else:
                    QtGui.QMessageBox.warning(
                        self, 'Warning',
                        'Sorry, no default parameters supplied to user defined function')


            def okButtonClicked(self):
                kwInitPara = {}
                for para in self.lineEditDict:
                    kwInitPara[para] = eval(str(self.lineEditDict[para].text()))
                self.pars = mod.make_params(**kwInitPara)
                self.close()


        dialog = ParaInputDialog(self)

        out = mod.fit(self.y, dialog.pars, x=self.x)

        self.DisplayResult(out)


    def UserDefinedFunctionFit(self):

        userDefinedFunctionList = [s for s in dir(UserDefinedFunction) if s[0].isupper()]

        d = QtGui.QInputDialog()
        func_name, ok = d.getItem(
            self, 'User Defined Function', 'Choose a function',
            userDefinedFunctionList)

        if ok:
            try:
                fun = getattr(UserDefinedFunction, str(func_name))
                # print fun
            except AttributeError:
                QtGui.QMessageBox.warning(
                    self, 'Warning',
                    'No such a function,\nplease check the name.')
                return
        else:
            return

        fun_model = Model(fun)
        self.Fitting(False, fun_model)

    def about_orange(self):
        pass


def main():
    QtCore.pyqtRemoveInputHook()
    app = QtGui.QApplication(sys.argv)
    orange = ApplicationWindow(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
