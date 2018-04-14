import argparse

from Data import Host, URL, Settings, Dir
from util import WebApi, logger, Content_Worker, Content, TERMINATE_WORKER

settings = None


class URL_Fuzzer:
    """class to perform spidering and fuzzing tasks"""

    def __init__(self, host):
        if type(host) is Host:
            self.host = host
        else:
            raise ValueError("wrong type for attribute host!")

        logger.info("fuzzing url", self.host.getURL())

    def spider(self):
        """
        spider-routine of the URL_Fuzzer
        return: None
        """

        logger.info("Spidering URL", self.host.getURL())
        rootcontent = Content(self.host.getURL())
        Content_Worker.queue.put(rootcontent)
        for i in range(0, Settings.readAttribute("recursion_depth",0)):
            logger.info('Processing recursion', i, Content_Worker.queue.qsize(), 'tasks to be done')
            Content_Worker.queue.join()

            while not Content_Worker.done.empty():
                content = Content_Worker.done.get()
                Content_Worker.done.task_done()
                if content.getStatus() in URL.GOOD_STATUS:
                    refs = WebApi.grabRefs(content.getContent())
                    rootURL = content.getURL()
                    for ref in refs:
                        try:
                            url = URL.prettifyURL(self.host, rootURL, ref)
                            if self.host.isExternal(url):
                                continue
                            newContent = Content(url)
                            path = url.getPath()
                            if len(path) == 0 or rootURL.getURL() == url.getURL():
                                continue
                            length = content.getSize()
                            self.host.getRootdir().appendPath(path, length)
                            Content_Worker.queue.put(newContent)
                        except ValueError as e:
                            continue

        self.host.getRootdir().printDirs()
        logger.info("spidering completed")

    

    def fuzz(self):
        logger.info("fuzzing URL", self.host.getURL())
        
        
        logger.info("fuzzing completed")



def startup():
    """
    initializes the program, writes all startup options in the Settings Object
    return: None
    """

    # parsing command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('url', metavar='url', help="the victims adress", type=str, nargs='+')
    parser.add_argument('-t', '--threads', help="the amount of threads to use", type=int, default=4)
    parser.add_argument('-r', '--recursion', help="the maximum recursion depth", type=int, default=5)
    parser.add_argument("-s", "--spider", action="store_true",
                        help="spider the given website")
    parser.add_argument("-f", "--fuzz", action="store_true", help="fuzz the given url to discover hidden files")
    parser.add_argument("--verifyCert", action="store_true", help="verify the hosts certificate")

    opts = parser.parse_args()

    # parse command line args
    host_url = opts.url[1]
    spider = opts.spider
    fuzz = opts.fuzz
    verify_cert = opts.verifyCert
    threads = opts.threads
    recursion_depth = opts.recursion

    # write attributes to Settings
    try:
        # check weither given URL is valid
        if not URL.isValidURL(host_url):
            raise ValueError(host_url + " is not a valid URL")

        Settings.writeAttribute("host_url",host_url)
        Settings.writeAttribute("spider",spider)
        Settings.writeAttribute("fuzz",fuzz)
        Settings.writeAttribute("verify_cert",verify_cert)
        Settings.writeAttribute("threads",threads)
        Settings.writeAttribute("recursion_depth",recursion_depth)

        WebApi.setProtocol(URL(Settings.readAttribute("host_url","")).getProto())
    except ValueError as e:
        raise e


def startWorkers(amount=4):
    """
    starts the workers
    attribute amount: the amount of workers to start
    return: None
    """

    logger.info("Starting " + str(amount) + " threads")
    for i in range(0, amount):
        c = Content_Worker()
        c.start()
        Content_Worker.workers.append(c)
    logger.info("Threads started")


def stopWorkers():
    """
    stops the running workers
    return: None
    """

    logger.info("stopping workers")
    for w in Content_Worker.workers:
        Content_Worker.queue.put(TERMINATE_WORKER)
    for w in Content_Worker.workers:
        w.join()

    logger.info("stopped workers")


def shutdown():
    """
    cleans up and stops the program
    return: None
    """

    try:
        stopWorkers()
    except:
        logger.error("failed to stop threads!")

    logger.info("finished scan")
    exit()


if __name__ == "__main__":

    try:
        startup()
        startWorkers(Settings.readAttribute("threads",4))
    except ValueError as e:
        logger.error(e)
        exit()

    targetHost = Host(
        URL(Settings.readAttribute("host_url","")), 
        Dir(Settings.readAttribute("root_dir",""),[],[])
        )

    urlFuzzer = URL_Fuzzer(targetHost)

    if Settings.readAttribute("spider",False):
        urlFuzzer.spider()

    if Settings.readAttribute("fuzz",False):
        urlFuzzer.fuzz()

    shutdown()
