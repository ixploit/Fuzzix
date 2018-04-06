import argparse

from util import logger, Content_Worker, Content
from Data import Host, Dir, File, URL, NONE_FILE
from Data import Settings
from util import WebApi

settings = None


class URL_Fuzzer:
    """class to perform spidering and fuzzing tasks"""

    def __init__(self,host):
        if type(host) is Host:
            self.host = host
        else:
            raise ValueError("wrong type for attribute host!")

        logger.info("fuzzing url",self.host.getURL())

    def spider(self):
        logger.info("Spidering URL",self.host.getURL())
        rootcontent=Content(self.host.getURL())
        Content_Worker.queue.put(rootcontent)
        for i in range(0,settings.getRecursion()):
            logger.info('Processing recursion',i)
            Content_Worker.queue.join()

            while not Content_Worker.done.empty():
                content = Content_Worker.done.get()
                if content.getStatus() in URL.GOOD_STATUS:
                    refs = WebApi.grabRefs(content.getContent())
                    rootURL=content.getURL()
                    for ref in refs:
                        try:
                            url = URL.prettifyURL(self.host,ref)
                            if self.host.isExternal(url):
                                continue
                            newContent = Content(url)
                            path = url.getPath()
                            if len(path) == 0 or rootURL.getURL() == url.getURL():
                                continue
                            length = content.getSize()
                            self.host.getRootdir().appendPath(path,length)
                            Content_Worker.queue.put(newContent)
                        except ValueError as e:
                            logger.error(e)
                            pass

        self.host.getRootdir().printDirs()
        logger.info("spidering completed")
    def fuzz(self):
        logger.info("fuzzing URL",self.host.getURL())

def startup():
    """
    return: attribute of class Settings containing all startup options
    """

    global settings

    #parsing command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('url',metavar='url',help="the victims adress",type=str,nargs='+')
    parser.add_argument('-t','--threads',help="the amount of threads to use",type=int,default=4)
    parser.add_argument('-r','--recursion',help="the maximum recursion depth",type=int,default=5)
    parser.add_argument("-s", "--spider", action="store_true",
                    help="spider the given website")
    parser.add_argument("-f","--fuzz",action="store_true",help="fuzz the given url to discover hidden files")
    parser.add_argument("--verifyCert",action="store_true",help="verify the hosts certificate")

    opts= parser.parse_args()

    #host
    host_url = opts.url[1]

    #spider
    spider = opts.spider

    #fuzz
    fuzz = opts.fuzz

    #verifyCert
    verifyCert = opts.verifyCert

    #threads
    threads = opts.threads

    #recursion
    recursion = opts.recursion
    
    try:
        settings = Settings(spider,fuzz,host_url,verifyCert,threads,recursion)
        WebApi.setProtocol(settings.getURL().getProto())
    except ValueError as e:
        raise e

def startWorkers(amount=4):
    logger.info("Starting " + str(amount) + " threads")
    for i in range(0,amount):
        c = Content_Worker()
        c.start()
        Content_Worker.workers.append(c)
    logger.info("Threads started")

if __name__ == "__main__":
   
    try:
        startup()
        startWorkers(settings.getThreads())
    except ValueError as e:
        logger.error(e)
        exit()
   
    targetHost = Host(settings.getURL(),settings.getRootDir())
    urlFuzzer = URL_Fuzzer(targetHost)

    if settings.getSpider():
        urlFuzzer.spider()

    if settings.getFuzz():
        urlFuzzer.fuzz()

    logger.info("Scan completed")

