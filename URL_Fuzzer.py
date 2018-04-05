import argparse

from util import logger
from Data import Host, Dir, File, NONE_FILE
from Data import Settings
from util import WebApi

settings = None


class URL_Fuzzer:
    """class to perform the spidering and fuzzing tasks"""

    def __init__(self,host):
        if type(host) is Host:
            self.host = host
        else:
            raise ValueError("wrong type for attribute host!")

        logger.info("fuzzing url",self.host.getURL())

    def spider(self):
        logger.info("Spidering URL",self.host.getURL())
        status,content = WebApi.receiveContent(self.host,self.host.getRootdir(),NONE_FILE)
        WebApi.grabRefs(content)

    def fuzz(self):
        logger.info("fuzzing URL",self.host.getURL())

def startup():
    """
    return:
    """

    global settings

    #parsing command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('url',metavar='url',help="the victims adress",type=str,nargs='+')
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
    
    try:
        settings = Settings(spider,fuzz,host_url,verifyCert)
        WebApi.setProtocol(settings.getURL().getProto())
    except ValueError as e:
        raise e


if __name__ == "__main__":
   
    try:
        startup()
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

