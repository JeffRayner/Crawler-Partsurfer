import re, csv
from threading import Thread, Lock
from urllib.request import urlopen
from bs4 import BeautifulSoup
import logging as log

log.basicConfig(filename='LOG.txt', level=log.DEBUG,
                format='%(levelname)s:%(message)s')

class PartSurfer:
    __id_PartNumber_Html = 'ctl00_BodyContentPlaceHolder_lblProductNumber'
    __id_SerialNumber_Html = 'ctl00_BodyContentPlaceHolder_lblSerialNumber'
    __id_ModelName_Html = 'ctl00_BodyContentPlaceHolder_lblDescription'
    __regex_Id_AllCategorys_Html = re.compile('ctl00_BodyContentPlaceHolder_rptRoot_ctl(.+)_KeywordLabel')
    __regex_Id_AllPartNumbers_Html = re.compile('ctl00_BodyContentPlaceHolder_rptRoot_ctl(.+)_gvProGeneral_ctl(.+)_lnkPartno')
    __regex_Id_AllDescriptions_Html = re.compile('ctl00_BodyContentPlaceHolder_rptRoot_ctl(.+)_gvProGeneral_ctl(.+)_lbldesc')
    __url = 'https://partsurfer.hpe.com/Search.aspx?SearchText='
    
    __threadList = []

    __columns_list_Export = ['Model PartNumber ', 'Model Name', 'Category', 'PartNumber', 'Description']
    __partNumbers_list = []
    __partNumbers_data = {}

    __lock = Lock()

    def __init__(self, partNumberList:str):
        self.__partNumbers_list = self.__extractListfromText(partNumberList)
    

    # PRIVATE METHODS
    def __extractListfromText(self, txtWithPartNumbers:str, separetor:str=',')->list:
        partNumberList = [ iten.strip() for iten in txtWithPartNumbers.replace('\n',',').split(separetor) ]
        return partNumberList

    
    def __resquestURL(self, partNumber:str):
        """Request URL with Parameter and call ValidadeHtmlPage() with the result"""

        with urlopen(self.__url + partNumber) as html:
            html = BeautifulSoup(html.read(), 'html.parser')
        self.__validateHtmlPage(html, partNumber)

    
    def __validateHtmlPage(self, html:BeautifulSoup, partNumber:str):
        """Check if ussed S/N and call resquestURL() or call scrapy() with the PartNumber and Html """
        
        try:
            find_serialNumber= html.find('span', id=self.__id_SerialNumber_Html)
            find_partNumber = html.find('span', id=self.__id_PartNumber_Html).get_text()
            if find_serialNumber:
                log.info( '{} - CHANGE TO:{}'.format(partNumber, find_partNumber) )
                self.__resquest_URL(find_partNumber)
        except Exception as e:
            log.warning( '{} - NOT FOUND'.format(partNumber) )
            return
        
        self.__scrapy(html, partNumber)


    def __scrapy(self, html:BeautifulSoup, partNumber:str,):
        """Search values in page and check the result has the same length and call formatingDataScrapy() with the values"""

        modelName = html.find('span', id=self.__id_ModelName_Html).get_text()
        categorysList = html.find_all('span', id=self.__regex_Id_AllCategorys_Html)
        partNumbersList = html.find_all('a', id=self.__regex_Id_AllPartNumbers_Html)
        descriptionsList = html.find_all('span', id=self.__regex_Id_AllDescriptions_Html)

        if len(descriptionsList) == len(partNumbersList):
            self.__formatingDataScrapy(modelName, partNumber, categorysList, partNumbersList, descriptionsList)
        else:
            log.debug( 'INDEX ERROR:{}'.format(partNumber) )
        
    
    def __formatingDataScrapy(self, modelName:str, partNumber:str, ctgList:list, pnList:list, descList:list):
        """Formating all values reciev to a List and call exportExcel() with the result"""

        data = []
        ctgList = [ i.get_text() for i in ctgList ]
        descList = [ i.get_text() for i in descList ]
        
        index_partN = []
        for i in pnList:
            ind = re.findall(self.__regex_Id_AllPartNumbers_Html, i['id'])[0]
            ind = ( int(ind[0]), int(ind[1]) )
            index_partN.append( ind )

            cat = ctgList[ ind[0] ]
            pn = i.get_text()
            desc = descList[index_partN.index(ind)].replace('\n','').rstrip(' ;')

            data.append([partNumber, modelName, cat, pn, desc])
        
        self.__lock.acquire()
        self.__partNumbers_data[partNumber] = data

        self.__lock.release()
        log.debug( '{} - OK'.format(partNumber) )


    # PUBLICS METHODS
    def find(self):
        for partnumber in self.__partNumbers_list:
            thread = Thread(target=self.__resquestURL, args=(partnumber,), daemon=True)
            self.__threadList.append(thread)
            thread.start()

        for thread in self.__threadList:
            thread.join()
        print ('Done.')
    

    def export2Csv(self, fileName:str):
        """Save a Data List in a CSV File"""

        data = self.__partNumbers_data
        with open(fileName+'.csv', 'w', encoding='UTF8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.__columns_list_Export)
            for row in data.values():
                writer.writerows(row)
        print('saved.')



#Part Numbers to test
#txt = '310587-201, 322470-001, 378739-201, 411597-201, 491505-201'
