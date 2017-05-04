# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ECOPluvia
                                 A QGIS plugin
 Esta ferramenta facilita a aquisição de dados de precipitação disponíveis no Portal HidroWeb.
                              -------------------
        begin                : 2016-01-25
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Jessica Fontoura , Daniel Allasia, Vitor Geller, Jean Favaretto, Gabriel Froemming, Robson Leo Pachaly 
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
from PyQt4 import QtGui
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from eco_pluvia_downloader_dialog import ECOPluviaDialog
from qgis.utils import *
import os
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
        self.menu = self.tr(u'&ECO-Pluvia Downloader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ECO-Pluvia')
        self.toolbar.setObjectName(u'ECO-Pluvia')
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)
        
        #Pega o clique do botão fechar e conecta a função fechar
        self.dlg.fechar.clicked.connect(self.fechar)
        self.dlg.okay.clicked.connect(self.run)
        
       
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
        return QCoreApplication.translate('ECO-Pluvia', message)


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
            text=self.tr(u'ECO-Pluvia'),
            callback=self.inicio,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ECO-Pluvia Downloader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
#=====================================================================================================================================#
    #Seleciona o diretório de saída
    def select_output_file(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "Salvar como ","", '*.txt')
        self.dlg.lineEdit.setText(filename)
    
    #Função para fechar a janela do plugin    
    def fechar(self):
        self.dlg.close()
        
    #Função de buscar o caminho do plugin
    def getCam(self):
        plugin_path = os.path.dirname(os.path.realpath(__file__))
        return plugin_path
    
    #Função de buscar o caminho escolhido pelo usuário
    def getCamUsu(self):
        path_to_file = self.dlg.lineEdit.text()
        return path_to_file
                    
    #chama a classe Hidroweb atribuindo as variaveis obtidas anteriormente            
        
    #Função de abertura da janela do plugin
    def inicio(self):
        
        #busca o caminho do plugin pela função
        plugin_path = self.getCam()
        #Abrir o shape das estacoes que está na pasta do plugin
        gages_layer = QgsVectorLayer(plugin_path, "Estacoes_ANA", "ogr")
        layerMap = QgsMapLayerRegistry.instance().mapLayers()
        #Se já tem um layer das estações carregado ele apaga
        for name, layer in layerMap.iteritems():
            if "Estacoes_ANA" in name:
                QgsMapLayerRegistry.instance().removeMapLayer(layer)
        #Adiciona a Layer gages ao mapa
        QgsMapLayerRegistry.instance().addMapLayer(gages_layer)
        #Ativa os layers adicionados ao canvas
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        self.dlg.comboBox.clear()
        self.dlg.comboBox.addItems(layer_list)  #preenche a comboBox com a lista dos layers
        
        selectedLayerIndex = self.dlg.comboBox.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        fields = selectedLayer.pendingFields()
        fieldnames = [field.name() for field in fields]
        self.dlg.comboBox_2.clear()
        self.dlg.comboBox_2.addItems(fieldnames) #preenche a comboBox_2 com a lista dos campos do layer selecionado
        self.dlg.show()
                                    
 #=================================================================================================================================================#
         
    def run(self):
        """Run method that performs all the real work"""        

        filename = self.dlg.lineEdit.text()
        if filename == '':
            self.iface.messageBar().pushMessage("ERRO", "Indique um diretorio para download dos dados!", level=QgsMessageBar.CRITICAL)
            return None
        else:
            output_file = open(filename, 'w')
            self.pathname = os.path.dirname(filename) #define o diretorio onde os arquivos serao baixados. Salva no mesmo diretorio do arquivo de texto
            #ativa os layers adicionados ao canvas
            layers = self.iface.legendInterface().layers()
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            selectedLayer = layers[selectedLayerIndex]
            selected_features = selectedLayer.selectedFeatures()
            
            valores =[]
           
            for f in selected_features:
                line = '%d' % (f['Codigo']) 
                lista = '%d\n' % (f['Codigo'])
                valores.append(line)
                output_file.write(lista)
            output_file.close()
            self.rodarHidroWeb(valores) #rodar funcao "rodarHidroWeb"
            
    def rodarHidroWeb(self,valores): 
        
        filename = self.dlg.lineEdit.text()
        path = os.path.dirname(filename)
        hid = Hidroweb(valores, path)
        hid.executar() 
        
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
        
        return (self.pathname + '/{0}.zip'.format(estacao))

    def salvar_arquivo_texto(self, estacao, link):
        r = requests.get(self.montar_url_arquivo(link), stream=True)
        if r.status_code == 200:
            with open(self.montar_nome_arquivo(estacao), 'wb') as f:
            
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                
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