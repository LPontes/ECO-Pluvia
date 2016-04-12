# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ECOPluvia
                                 A QGIS plugin
 Esta ferramenta facilita a aquisição de dados de precipitação disponíveis no Portal HidroWeb.
                              -------------------
        begin                : 2016-01-25
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Jessica Fontoura 
        email                : jessica.ribeirofontoura@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog  
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from eco_pluvia_downloader_dialog import ECOPluviaDialog
import os.path
import requests
import re
import shutil
from bs4 import BeautifulSoup

class ECOPluvia:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ECOPluvia_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ECOPluviaDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ECO Pluvia Downloader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ECOPluvia')
        self.toolbar.setObjectName(u'ECOPluvia')
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)
		

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ECOPluvia', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ECOPluvia/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ECO Pluvia'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ECO Pluvia Downloader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    def select_output_file(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ","", '*.txt')
        self.dlg.lineEdit.setText(filename)
        #diretorio_saida = filename.split("/") #provisorio
        

    def run(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        self.dlg.comboBox.clear()
        self.dlg.comboBox.addItems(layer_list)
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            filename = self.dlg.lineEdit.text()
            output_file = open(filename, 'w')
            
            self.pathname = os.path.dirname(filename) #define o diretorio onde os arquivos serao baixados. Salva no mesmo diretorio do arquivo de texto
            
          
            #os.chdir(pathname)
            
            
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            selectedLayer = layers[selectedLayerIndex]
            #fields = selectedLayer.pendingFields()
            #fieldnames = [field.name() for field in fields]
            selected_features = selectedLayer.selectedFeatures()
            
            valores =[]
            #for f in selectedLayer.selectedFeatures():
            for f in selected_features:
                #selected_features = selectedLayer.selectedFeatures
                #line = ','.join(unicode(f[x]) for x in fieldnames) + '\n'
                #unicode_line = line.encode('utf-8')
                line = '%d' % (f['Codigo']) #%i
                lista = '%d\n' % (f['Codigo'])
                
                #valores.append(line.encode('utf-8'))
                valores.append(line)
                output_file.write(lista)
            output_file.close()
            self.rodarHidroWeb(valores) #rodar funcao "rodarHidroWeb"
            
    def rodarHidroWeb(self,valores):
        
        hid = Hidroweb(valores, self.pathname)
        hid.executar()        
#### By Arthurimport os       
class Hidroweb(object):

    url_estacao = 'http://hidroweb.ana.gov.br/Estacao.asp?Codigo={0}&CriaArq=true&TipoArq={1}'
    url_arquivo = 'http://hidroweb.ana.gov.br/{0}'

    def __init__(self, estacoes, pathname):
        self.estacoes = estacoes
        self.pathname = pathname

    def montar_url_estacao(self, estacao, tipo=1):
        return self.url_estacao.format(estacao, tipo)

    def montar_url_arquivo(self, caminho):
        return self.url_arquivo.format(caminho)

    def montar_nome_arquivo(self, estacao):
        #self.pathname
        #return u'{0}.zip'.format(estacao)
        return (self.pathname + '/{0}.zip'.format(estacao))

    def salvar_arquivo_texto(self, estacao, link):
        r = requests.get(self.montar_url_arquivo(link), stream=True)
        if r.status_code == 200:
            with open(self.montar_nome_arquivo(estacao), 'wb') as f:
            #with open(self.montar_nome_arquivo(estacao), 'w') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                #shutil.copyfile(r.raw, f)
            print '** %s ** (Baixando)' % (estacao, )
        else:
            print '** %s ** (Problema)' % (estacao, )

    def obter_link_arquivo(self, response):
        soup = BeautifulSoup(response.content)
        return soup.find('a', href=re.compile('^ARQ/'))['href']

    def executar(self):
        
        post_data = {'cboTipoReg': '10'}
        for est in self.estacoes:
            try:
                print '** %s ** - Procurando dados...' % (est, )
                r = requests.post(self.montar_url_estacao(est), data=post_data)
                link = self.obter_link_arquivo(r)
                self.salvar_arquivo_texto(est, link)
                print '** %s ** (Concluido)' % (est, )
            except:
                print '** %s ** - ERRO: Estacao nao possui dados.\n' % (est, )
