"""
***************************************************************************
    ClipVectorByMask.py
    ---------------------
    Date                 : November 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'November 2012'
__copyright__ = '(C) 2012, Victor Olaya'

from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorDestination)
from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils


class ClipVectorByMask(GdalAlgorithm):
    INPUT = 'INPUT'
    MASK = 'MASK'
    OPTIONS = 'OPTIONS'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def flags(self):
        return QgsProcessingAlgorithm.Flag.FlagSupportsBatch | QgsProcessingAlgorithm.Flag.FlagRequiresMatchingCrs  # cannot cancel!

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterFeatureSource(self.MASK,
                                                              self.tr('Mask layer'),
                                                              [QgsProcessing.SourceType.TypeVectorPolygon]))

        options_param = QgsProcessingParameterString(self.OPTIONS,
                                                     self.tr('Additional creation options'),
                                                     defaultValue='',
                                                     optional=True)
        options_param.setFlags(options_param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        self.addParameter(options_param)

        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT,
                                                                  self.tr('Clipped (mask)')))

    def name(self):
        return 'clipvectorbypolygon'

    def displayName(self):
        return self.tr('Clip vector by mask layer')

    def group(self):
        return self.tr('Vector geoprocessing')

    def groupId(self):
        return 'vectorgeoprocessing'

    def commandName(self):
        return 'ogr2ogr'

    def getConsoleCommands(self, parameters, context, feedback, executing=True):
        inLayer, inLayerName = self.getOgrCompatibleSource(self.INPUT, parameters, context, feedback, executing)
        maskLayer, maskLayerName = self.getOgrCompatibleSource(self.MASK, parameters, context, feedback, executing)
        options = self.parameterAsString(parameters, self.OPTIONS, context)
        outFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        self.setOutputValue(self.OUTPUT, outFile)

        output, outputFormat = GdalUtils.ogrConnectionStringAndFormat(outFile, context)

        arguments = [
            '-clipsrc',
            maskLayer,
            '-clipsrclayer',
            maskLayerName,

            output,
            inLayer,
            inLayerName,
        ]

        if options:
            arguments.append(options)

        if outputFormat:
            arguments.append(f'-f {outputFormat}')

        return [self.commandName(), GdalUtils.escapeAndJoin(arguments)]
