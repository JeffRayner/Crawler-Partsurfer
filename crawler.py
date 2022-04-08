import re, pandas, xlsxwriter
from threading import Thread, Lock
from urllib.request import urlopen
from bs4 import BeautifulSoup
import logging as log

log.basicConfig(filename='LOG.txt', level=log.DEBUG,
                format='%(levelname)s:%(message)s')

class PartSurfer:
    id_PartNumber_Html = 'ctl00_BodyContentPlaceHolder_lblProductNumber'
    id_SerialNumber_Html = 'ctl00_BodyContentPlaceHolder_lblSerialNumber'
    id_ModelName_Html = 'ctl00_BodyContentPlaceHolder_lblDescription'
    regex_Id_AllCategorys_Html = re.compile('ctl00_BodyContentPlaceHolder_rptRoot_ctl(.+)_KeywordLabel')
    regex_Id_AllPartNumbers_Html = re.compile('ctl00_BodyContentPlaceHolder_rptRoot_ctl(.+)_gvProGeneral_ctl(.+)_lnkPartno')
    regex_Id_AllDescriptions_Html = re.compile('ctl00_BodyContentPlaceHolder_rptRoot_ctl(.+)_gvProGeneral_ctl(.+)_lbldesc')
    url = 'https://partsurfer.hpe.com/Search.aspx?SearchText='
    
    threadList = []
    partNumbers_data = {}

    lock = Lock()

    def __init__(self, partNumberList:str, excelName:str='Result'):
        partNumberList = self.extractListfromText(partNumberList)
        for partNumber in partNumberList:
            thread = Thread(target=self.resquestURL, args=(partNumber,), daemon=True)
            self.threadList.append(thread)
            thread.start()

        for thread in self.threadList:
            thread.join()
        
        self.exportExcel(self.partNumbers_data, excelName)
        print('\n','IT\'S OVER','\n')


    def extractListfromText(self, txtWithPartNumbers:str, separetor:str=',')->list:
        partNumberList = [iten.strip() for iten in txtWithPartNumbers.split(separetor)]
        return partNumberList

    
    def resquestURL(self, partNumber:str):
        """Request URL with Parameter and call ValidadeHtmlPage() with the result"""

        with urlopen(self.url + partNumber) as html:
            html = BeautifulSoup(html.read(), 'html.parser')
        self.validateHtmlPage(html, partNumber)

    
    def validateHtmlPage(self, html:BeautifulSoup, partNumber:str):
        """Check if ussed S/N and call resquestURL() or call scrapy() with the PartNumber and Html """
        
        try:
            find_serialNumber= html.find('span', id=self.id_SerialNumber_Html)
            find_partNumber = html.find('span', id=self.id_PartNumber_Html).get_text()
            if find_serialNumber:
                log.info( '{} - CHANGE TO:{}'.format(partNumber, find_partNumber) )
                self.resquest_URL(find_partNumber)
        except Exception as e:
            log.warning( '{} - NOT FOUND'.format(partNumber) )
            return

        self.scrapy(html, partNumber)


    def scrapy(self,  html:BeautifulSoup, partNumber:str,):
        """Search values in page and check the result has the same length and call formatingDataScrapy() with the values"""

        modelName = html.find('span', id=self.id_ModelName_Html).get_text()
        categorysList = html.find_all('span', id=self.regex_Id_AllCategorys_Html)
        partNumbersList = html.find_all('a', id=self.regex_Id_AllPartNumbers_Html)
        descriptionsList = html.find_all('span', id=self.regex_Id_AllDescriptions_Html)

        if len(descriptionsList) == len(partNumbersList):
            self.formatingDataScrapy(modelName, partNumber, categorysList, partNumbersList, descriptionsList)
        else:
            log.debug( 'INDEX ERROR:{}'.format(partNumber) )
        
    
    def formatingDataScrapy(self, modelName:str, partNumber:str, ctgList:list, pnList:list, descList:list):
        """Formating all values reciev to a List and call exportExcel() with the result"""

        index_categoria = [re.findall(self.regex_Id_AllCategorys_Html, i['id'])[0] for i in ctgList]
        index_partN = [re.findall(self.regex_Id_AllPartNumbers_Html, i['id'])[0] for i in pnList]
        index_desc = [re.findall(self.regex_Id_AllDescriptions_Html, i['id'])[0] for i in descList]
        data = []
        for i in index_desc:
            id0 = index_categoria.index(i[0])
            id1 = index_partN.index(i)
            id2 = index_desc.index(i)
            data.append([partNumber, modelName, ctgList[id0].text, pnList[id1].text, descList[id2].text])

        self.lock.acquire()

        self.partNumbers_data[partNumber] = data

        self.lock.release()
        log.debug( '{} - OK'.format(partNumber) )


    def exportExcel(self, dataList:dict, fileName:str):
        """Save an Excel File with Part Numbers'name of equipament"""
        
        colums = ['Part Number', 'Model Name', 'Category', 'PartNumber', 'Description']
        file = pandas.ExcelWriter(fileName+'.xlsx', engine='xlsxwriter')

        for partNumber in dataList:
            aba = pandas.DataFrame(data=dataList[partNumber] , columns=colums)
            aba.to_excel(file, sheet_name=partNumber, index=False)
        
        file.save()





if __name__ == '__main__':
    txt = ('310587-201, 322470-001, 378739-201, 411597-201, 491505-201')
    PartSurfer(txt)