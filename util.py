import urllib3
urllib3.disable_warnings()
import re
from coloredlogger import ColoredLogger
from bs4 import BeautifulSoup

logger = ColoredLogger(name="MAIN")

from Data import URL
from Data import HTTP, HTTPS
from Data import Host
from Data import Dir
from Data import File

class __WebApi__:

    def __init__(self, protoName):
        
        try:
            self.setProtocol(protoName)
            self.poolManager = urllib3.PoolManager()

        except ValueError as e:
            raise e
    
    def setProtocol(self,protoName):
        try:
            self.proto = HTTP.getProtocol(protoName)
        except ValueError as e:
            raise e

    def receiveContent(self,host,dir,file):
        if type(dir) is not Dir:
            raise ValueError('unsupported type for attribute dir')
        if type(file) is not File:
            raise ValueError('unsupported type for attribute file')
        if type(host) is not Host:
            raise ValueError('unsupported type for attribute host')

        url = URL.buildURL(host.getURL().getProto(),host.getURL().getHost(),host.getURL().getPort(),dir.getName(),file.getName())
        r = self.poolManager.request('GET',url)
        
        return r.status, str(BeautifulSoup(r.data, 'html.parser'))


    def grabRefs(self,content):
        """
        attribute content: a str encoded html document
        return: returns the extracted links
        """
        results=[]
        page = BeautifulSoup(content, 'html.parser')

        #divide in tags
        tags = page.find_all()
        #scanning src attribute
        for tag in tags:
            link = tag.get('src')
            if link is not None:
                print(link)

        #scanning href attribute
        for tag in tags:
            link = tag.get('href')
            if link is not None:
                print(link)


WebApi = __WebApi__('HTTP')