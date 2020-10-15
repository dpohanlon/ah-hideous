import json
import argparse

import numpy as np

from scipy.stats import multivariate_normal

import uproot

import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.use('Agg')
plt.style.use(['seaborn-whitegrid', 'seaborn-ticks'])

def generateTestData(n, plot = True):

    ''' nxn bins of some nice Normal distributions '''

    norm1 = multivariate_normal([3.0, 3.0], [[2 ** 2, 0], [0, 2 ** 2]])
    norm2 = multivariate_normal([-3.0, -3.0], [[3 ** 2, 0], [0, 3 ** 2]])

    x = np.linspace(-10, 10, n)
    y = np.linspace(-10, 10, n)
    xv, yv = np.meshgrid(x, y)

    gridVals = np.stack((xv, yv), 2)
    vals = norm1.pdf(gridVals) + norm2.pdf(gridVals)

    if plot:
        plt.imshow(vals, origin = 'lower', cmap = 'viridis')
        plt.savefig('testData.pdf')
        plt.clf()

    return vals

def histFromROOTFile(fileName, histName):

    f = uproot.open(fileName)

    # NumPy hist format -> (bin contents, bin edges)
    h = f[histName].numpy()

    return h

def scale(hist, scalingParam = 15):

    '''
    Scale the histogram according to the maximum bin height. A scale of ~15
    gives a reasonable aspect ratio for a 20x20 grid.

    '''

    return scalingParam * (hist / np.amax(hist))

def writeJSONHist(hist, outFileName, scalingParam, doScaling = True):

    if doScaling:
        hist = scale(hist, scalingParam)

    json.dump(hist.tolist(), open(outFileName, 'w'), indent = 4)

if __name__ == '__main__':

    argParser = argparse.ArgumentParser()

    argParser.add_argument("-rf", "--rootFile", type = str, dest = "rootFile", default = None, help = 'ROOT file path.')
    argParser.add_argument("-rh", "--rootHist", type = str, dest = "rootHist", default = None, help = 'ROOT histogram path.')
    argParser.add_argument("-o", "--outFile", type = str, dest = "outFile", default = "hist.json", help = 'Output histogram JSON file name.')

    argParser.add_argument("-t", "--test", dest = "test", action = "store_true", default = False, help = 'Generate test data.')

    argParser.add_argument("-s", "--scale", type = float, dest = "scale", default = 15, help = 'Height of the highest bin.')

    args = argParser.parse_args()

    if args.rootFile and args.rootHist:
        hist = histFromROOTFile(args.rootFile, args.rootHist)
        writeJSONHist(hist[0], args.outFile, args.scale)

    if args.test:
        hist = generateTestData(50)
        writeJSONHist(hist, args.outFile, args.scale)
