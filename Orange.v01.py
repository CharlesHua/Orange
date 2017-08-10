#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Data dispaly in sheet and image

@author: Jiannan Hua 
last edited: Aug. 5 2017
"""

import sys, random, numpy
#import matplotlib
#import matplotlib.pyplot as plt
import numpy as np
from numpy import loadtxt
from scipy.optimize import *  #leastsq, curve_fit
#from scipy.optimize import curve_fit
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import * 
from PyQt4.QtCore import *
from matplotlib.backends import qt_compat
from numpy import arange, sin, pi, sqrt, exp
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from lmfit.models import * #GaussianModel, LorentzianModel, ConstantModel

def gaussian_plus_line(x, amp, cen, wid, slope, intercept):
    print  amp, cen, wid, slope, intercept
   # gauss = (amp/(sqrt(2*pi)*wid)) * exp(-(x-cen)**2 /(2*wid**2))
    line = slope * x + intercept
    print line
    return  line


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        print 'initial_figure'
        x = numpy.random.randn(20)
        z = numpy.random.randn(20)
        #sprint x
        self.axes.scatter(x, z)



def LinearFunction(x, k, b):
    # k = arg[0]
    # b = arg[1]
    # print 'L=',para
    return k * x + b

def QuadraticFunction(x, a,b,c):
    return a * x ** 2 + b * x + c

def LorentzianFunction(x, I , x0, gamma):
    # I , x0, gamma = para
    # print 'Lo=',para
    return I / ( 1 + ((x - x0) / gamma)**2)    


class ApplicationWindow(QtGui.QMainWindow):
    """docstring for ApplicationWindow"""
    def __init__(self, arg):
        super(ApplicationWindow, self).__init__()
        self.arg = arg
        self.Init_Data()
        self.Init_Ui()

    def Init_Data(self):
        self.length = 0
        self.x = [0,]
        self.y = [0,]

    def Init_Ui(self):

        #statusBar and menuBar
        self.statusBar()
        menubar = self.menuBar()
        
        openFileAction = QtGui.QAction(QtGui.QIcon('open.png'), 'Open File...', self)
        openFileAction.setShortcut('Ctrl+O')
        openFileAction.setStatusTip('Open New File')
        openFileAction.triggered.connect(self.OpenFile)

        linearFitAction = QtGui.QAction(QtGui.QIcon(''), 'Linear Fit', self)
        linearFitAction.setStatusTip('FitLinear: linear regression on XY data')
        linearFitAction.triggered.connect(lambda: self.Fitting_New( LinearModel() ))

        quadraticFitAction = QtGui.QAction(QtGui.QIcon(''), 'Quadratic Fit', self)
        quadraticFitAction.setStatusTip('FitQuadratic: quadratic regression on XY data')
        quadraticFitAction.triggered.connect(lambda: self.Fitting_New( QuadraticModel() ))

        lorentzianFitAction = QtGui.QAction(QtGui.QIcon(''), 'Lorentzian Fit', self)
        lorentzianFitAction.setStatusTip('FitLorentzian: Lorentzian regression on XY data')
        lorentzianFitAction.triggered.connect(lambda: self.Fitting_New( LorentzianModel() ))

        lorentzianFitWithBaseAction = QtGui.QAction(QtGui.QIcon(''), 'Lorentzian Fit With Base', self)
        lorentzianFitWithBaseAction.setStatusTip('FitLorentzianWithBase: Lorentzian regression on XY data')
        lorentzianFitWithBaseAction.triggered.connect(self.Fit)

        gaussianFitAction = QtGui.QAction(QtGui.QIcon(''), 'Gaussian Fit', self)
        gaussianFitAction.setStatusTip('FitGaussian: Gaussian regression on XY data')
        gaussianFitAction.triggered.connect(lambda: self.Fitting_New( GaussianModel() ))

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFileAction)
        analysisMenu = menubar.addMenu('&Analysis')
        analysisMenu.addAction(linearFitAction)
        analysisMenu.addAction(quadraticFitAction)
        analysisMenu.addAction(lorentzianFitAction)
        analysisMenu.addAction(lorentzianFitWithBaseAction)
        analysisMenu.addAction(gaussianFitAction)


        # data table and picture
    #    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.table = QtGui.QTableWidget()
        self.table.setRowCount(5)
        self.table.setColumnCount(2)
    # set label
        self.table.setHorizontalHeaderLabels(QString("X;Y").split(";"))
    # set data
        newItem =  QTableWidgetItem('0')
        newItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(0,0, newItem)
        newItem =  QTableWidgetItem('0')
        newItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(0,1, newItem)
     #   self.table.setItem(0,0, QTableWidgetItem("0"))
     #   self.table.setItem(0,1, QTableWidgetItem("0"))


    # tooltip text
        self.table.horizontalHeaderItem(0).setToolTip("Column 1 ")
        self.table.horizontalHeaderItem(1).setToolTip("Column 2 ")
        self.table.setFrameShape(QtGui.QFrame.StyledPanel)
 
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # on click function
      #  self.table.cellClicked.connect(self.cellClick)
 

      #  self.bottom = QtGui.QFrame(self)
      #  self.bottom.setFrameShape(QtGui.QFrame.StyledPanel)

        self.pictr = MyMplCanvas(width=5, height=4, dpi=100)
        self.pictr.axes.set_xlabel('X')
        self.pictr.axes.set_ylabel('Y')

        self.pictrErr = MyMplCanvas(width=5, height=2, dpi=100)
        self.pictrErr.axes.set_xlabel('X')
        self.pictrErr.axes.set_ylabel('Y.data-Y.exp')
        # self.pictrErr.subplots_adjust(bottom=0.2)

        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setReadOnly(True)

        splitterV = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterV.addWidget(self.pictr)
        splitterV.addWidget(self.pictrErr)
        splitterV.setStretchFactor(0, 5)
        splitterV.setStretchFactor(1, 4)

        splitterH = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitterH.addWidget(self.table)
        splitterH.addWidget(splitterV)
        splitterH.addWidget(self.textEdit)
       # splitter.setSizes([1, 20])
        splitterH.setStretchFactor(0, 0)
        splitterH.setStretchFactor(1, 3)
        splitterH.setStretchFactor(2, 0)
    	
    	self.setCentralWidget(splitterH)
        self.setGeometry(200, 100, 800, 600)
        self.setWindowTitle('Orange') 

        self.show()


    def OpenFile(self):

        fileAddress = QtGui.QFileDialog.getOpenFileName(self, 'Open file', directory = '')
        addstr = str(fileAddress)
        def ImportData(file):
            # print fileAddress
            # print file
            data = loadtxt(addstr)
            self.x = data[:, 0]
            self.y = data[:, 1]

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
            # 左对齐
                # self.table.setItem(i,0, QTableWidgetItem(str(self.x[i])))
                # self.table.setItem(i,1, QTableWidgetItem(str(self.y[i])))
            # 右对齐
                newItem =  QTableWidgetItem(str(self.x[i]))
                newItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i,0, newItem)
                newItem =  QTableWidgetItem(str(self.y[i]))
                newItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i,1, newItem)

        def DrawDataPoint():
            self.pictr.axes.cla()
            self.pictr.axes.set_xbound(min(self.x), max(self.x))
            self.pictr.axes.set_ybound(min(self.y), max(self.y))
            self.pictr.axes.scatter(self.x, self.y, c='k')

            self.pictr.draw()
            self.pictr.axes.set_xlabel('X')
            self.pictr.axes.set_ylabel('Y')

            self.linelist = []

            self.pictrErr.axes.cla()
            self.pictrErr.axes.set_xbound(self.pictr.axes.get_xbound())
            self.pictrErr.draw()

            self.repoter = ''
            self.textEdit.setText(self.repoter)


        #self.pictr.compute_initial_figure()
        
        f = open(fileAddress, 'r')
        with f:
            ImportData(f)
            DisplayInTable()
            DrawDataPoint()
            self.setStatusTip(fileAddress)


    def Fitting_New(self, mod):
        
        # try:
        #     pars = mod.guess(self.y, x = self.x)
        # except NotImplementedError as e:
        #     print 'No para'
        #     out  = mod.fit(self.y, x = self.x)
        # else:
        #     out  = mod.fit(self.y, pars, x = self.x)
        # finally:
        #     pass
        # out  = mod.fit(self.y, x = self.x)


        pars = mod.guess(self.y, x = self.x)
      #  pars  = mod.make_params( amp=5, cen=5, wid=1, slope=0, intercept=1)
        out  = mod.fit(self.y, pars, x = self.x)


        # not sure how tu use this
        # self.pictr.axes = out.plot_fit()
        
        #plt.plot(self.x, self.y,         'bo')
        #   self.pictr.axes.plot(self.x, out.init_fit, 'k--')

        xwide = np.linspace(min(self.x), max(self.x), 501)
        y_predicted = out.eval(x = xwide)


        newline, = self.pictr.axes.plot(xwide, y_predicted, label=str(mod.name))
        self.linelist.append(newline)
        self.pictr.axes.legend(handles=self.linelist, loc=1)

        self.pictr.draw()
        self.pictr.axes.set_xlabel('X')
        self.pictr.axes.set_ylabel('Y')

        # draw err picture
        self.pictrErr.axes.scatter(self.x, self.y - out.best_fit)
        self.pictrErr.axes.axhline(y=0, color='k', linestyle='--', linewidth=1.0)
        self.pictrErr.axes.set_xbound(self.pictr.axes.get_xbound())
        self.pictrErr.draw()
        self.pictrErr.axes.set_xlabel('X')
        self.pictrErr.axes.set_ylabel('Y.data - Y.exp')

        print 'out = ', out
        print 'N_varys =', out.nvarys
        print mod.param_names
        print 'nubmer of data points =', len(self.x)
        print 'n_free =', out.nfree
        print 'chi_sqre =', sum((out.best_fit-self.y)**2)
        print 'res_chi_sqre = ', sum((out.best_fit-self.y)**2)/out.nfree

        # print fit repoter
        self.repoter += out.fit_report() + '\n'
        self.textEdit.setText(self.repoter)

    def Fit(self):
        lorentz_mod = LorentzianModel()
        line_mod = LinearModel()

        pars =  line_mod.guess(self.y, x = self.x)
        pars += lorentz_mod.guess(self.y, x = self.x)

        mod = lorentz_mod + line_mod
        out = mod.fit(self.y, pars, x = self.x)

        xwide = np.linspace(min(self.x), max(self.x), 501)
        y_predicted = out.eval(x = xwide)

        newline, = self.pictr.axes.plot(xwide, y_predicted, label=str(mod.name))
        self.linelist.append(newline)
        self.pictr.axes.legend(handles=self.linelist, loc=1)
        self.pictr.draw()

        print 'out = ', out
        print 'N_varys =', out.nvarys
        print mod.param_names
        print 'nubmer of data points =', len(self.x)
        print 'n_free =', out.nfree
        print 'chi_sqre =', sum((out.best_fit-self.y)**2)
        print 'res_chi_sqre = ', sum((out.best_fit-self.y)**2)/out.nfree

        self.pictr.axes.set_xlabel('X')
        self.pictr.axes.set_ylabel('Y')

        self.repoter += out.fit_report() + '\n'
        self.textEdit.setText(self.repoter)

        # draw err picture
        self.pictrErr.axes.scatter(self.x, self.y - out.best_fit)
        self.pictrErr.axes.axhline(y=0, color='k', linestyle='--', linewidth=1.0)
        self.pictrErr.axes.set_xbound(self.pictr.axes.get_xbound())
        self.pictrErr.draw()
        self.pictrErr.axes.set_xlabel('X')
        self.pictrErr.axes.set_ylabel('Y.data - Y.exp')


def main():
    
    app = QtGui.QApplication(sys.argv)
    psd = ApplicationWindow(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()    