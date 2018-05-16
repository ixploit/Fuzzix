"""
serves different functions for webcrawling
"""
import threading
from queue import Queue

import urllib3
from bs4 import BeautifulSoup
from api import LOGGER
from api.data import URL, HTTP, Host, Dir, File
urllib3.disable_warnings()


class __WebApi__:
    def __init__(self, protoName):

        try:
            self.setProtocol(protoName)
            self.poolManager = urllib3.PoolManager()

        except ValueError as error:
            raise error

    def setProtocol(self, protoName):
        try:
            self.proto = HTTP.getProtocol(protoName)
        except ValueError as error:
            raise error

    def receiveURL(self, url):
        if type(url) is not URL:
            raise ValueError('unsopported type for attribute url')

        r = self.poolManager.request('GET', url.getURL())
        content = Content(url)
        content.setStatus(r.status)
        content.setContentType(r.getheaders()['Content-Type'])

        #check filetype
        if 'text' in r.getheaders()['Content-Type']:
            content.setContent(str(BeautifulSoup(r.data, 'html.parser')))
        else:
            content.setContent(r.data)
        return content

    def grabRefs(self, content):
        """
        extracts most hyperlinks out of a given html document
        attribute content: a str encoded html document
        return: returns the extracted links as a list
        """
        results = []
        page = BeautifulSoup(content, 'html.parser')

        # divide in tags
        tags = page.find_all()

        # scanning src attribute
        for tag in tags:
            link = tag.get('src')
            if link is not None:
                results.append(link)

        # scanning href attribute
        for tag in tags:
            link = tag.get('href')
            if link is not None:
                results.append(link)

        return results


WebApi = __WebApi__('HTTP')


class Content:
    """a class to represent content on a remote host"""

    def __init__(self, url):
        if type(url) is not URL:
            raise ValueError("invalid type for attribute url")

        self.url = url
        self.size = 0
        self.content = ""
        self.status = 0

    def getURL(self):
        return self.url

    def getSize(self):
        return len(self.getContent())

    def getContent(self):
        return self.content

    def getStatus(self):
        return self.status

    def getContentType(self):
        return self.contentType

    def setStatus(self, status):
        self.status = status

    def setContent(self, content):
        self.content = content

    def setContentType(self, contentType):
        self.contentType = contentType

    def setProcessor(self, processor):
        self.processor = processor

    def getProcessor(self):
        return self.processor


# object to tell the workers to terminate
TERMINATE_WORKER = Content(URL("http://TERMINA.TE"))


class ContentWorker(threading.Thread):
    """processes content attributes"""
    queue = Queue(maxsize=0)
    done = Queue(maxsize=0)
    workers = []

    def __init__(self):
        super().__init__()

    def run(self):
        """
        run-method of the thread
        return: None
        """
        while True:
            content = ContentWorker.queue.get()

            # stop when terminate signal received
            if content.getURL().getURL() == TERMINATE_WORKER.getURL().getURL():
                ContentWorker.queue.task_done()
                return

            try:
                func = content.getProcessor()
                content = WebApi.receiveURL(content.getURL())
                newContent = func(content)
                ContentWorker.done.put(newContent)
            except BaseException as error:
                LOGGER.error('catched exception ', error, 'in child-thread')
            except:
                LOGGER.error("fatal error in childthread")
            ContentWorker.queue.task_done()
