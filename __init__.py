# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ECOPluvia
                                 A QGIS plugin
 Esta ferramenta facilita a aquisição de dados de precipitação disponíveis no Portal HidroWeb.
                             -------------------
        begin                : 2016-01-25
        copyright            : (C) 2016 by Jessica Fontoura 
        email                : jessica.ribeirofontoura@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ECOPluvia class from file ECOPluvia.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .eco_pluvia_downloader import ECOPluvia
    return ECOPluvia(iface)
