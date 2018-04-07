import urllib3
urllib3.disable_warnings()



import threading
from queue import Queue
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

    def receiveURL(self,url):
        if type(url) is not URL:
            raise ValueError('unsopportd type for attribute url')
    
        r = self.poolManager.request('GET',url.getURL())
        return r.status, str(BeautifulSoup(r.data,'html.parser'))

    def grabRefs(self,content):
        """
        extracts most hyperlinks out of a given html document
        attribute content: a str encoded html document
        return: returns the extracted links as a list
        """
        results=[]
        page = BeautifulSoup(content, 'html.parser')

        #divide in tags
        tags = page.find_all()

        #scanning src attribute
        for tag in tags:
            link = tag.get('src')
            if link is not None:
                results.append(link)

        #scanning href attribute
        for tag in tags:
            link = tag.get('href')
            if link is not None:
                results.append(link)

        return results


WebApi = __WebApi__('HTTP')

class Content:
    """a class to represent content on a remote host"""

    def __init__(self,url):
        if type(url) is not URL:
            raise ValueError("invalid type for attribute url")

        self.url = url
        self.size = 0
        self.content=""
        self.status = 0

    def getURL(self):
        return self.url

    def getSize(self):
        return len(self.getContent())

    def getContent(self):
        return self.content

    def getStatus(self):
        return self.status

    def setStatus(self,status):
        self.status = status

    def setContent(self,content):
        self.content = content

#object to tell the workers to terminate
TERMINATE_WORKER = Content(URL("http://TERMINA.TE"))

class Content_Worker (threading.Thread):

    queue=Queue(maxsize=0)
    done=Queue(maxsize=0)
    workers=[]

    def __init__(self):
        return super().__init__()

    def run(self):
        """
        run-method of the thread
        return: None
        """
        while True:
            content = Content_Worker.queue.get()

            #stop when terminate signal received
            if content.getURL().getURL() == TERMINATE_WORKER.getURL().getURL():
                Content_Worker.queue.task_done()
                return

            try:
                status,htmlContent=WebApi.receiveURL(content.getURL())
                content.setContent(htmlContent)
                content.setStatus(status)
                Content_Worker.done.put(content)
            except:
                pass
            Content_Worker.queue.task_done()

