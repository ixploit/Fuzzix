import argparse

from Fuzzix.Data import Host, URL, Settings, Dir, Wordlist
from Fuzzix.Util import WebApi, Content_Worker, Content, TERMINATE_WORKER
from Fuzzix import Logger, print_banner


class URL_Fuzzer:
    """class to perform spidering and fuzzing tasks"""

    def __init__(self, host):
        if type(host) is Host:
            self.host = host
        else:
            raise ValueError("wrong type for attribute host!")

        Logger.info("fuzzing url", self.host.getURL())

    def __init_wordlists__(self):
        """
        reads the path of the wordlists out of the Settings and reads the wordlists into memory
        return: None
        """
        self.directories_wordlist = Wordlist("directories",
                                             Settings.readAttribute(
                                                 "WORDLISTS/directories", ""))
        self.ExtensionsWordlist = Wordlist("extension",
                                           Settings.readAttribute(
                                               "WORDLISTS/extensions", ""))
        self.FilesWordlist = Wordlist("files",
                                      Settings.readAttribute(
                                          "WORDLISTS/files", ""))
        self.mutationsWordlist = Wordlist("mutations",
                                          Settings.readAttribute(
                                              "WORDLISTS/mutations", ""))

    @staticmethod
    def __spiderworker__(content):
        """
        the function called by Util.Content_Worker to spider the given url
        attribute content: the content to proceed
        return: A proceeded content object
        """
        rootURL = content.getURL()
        newContent = Content(rootURL)
        newContent.setContentType(content.getContentType())
        newContent.setStatus(content.getStatus())

        if content.getStatus() in URL.GOOD_STATUS:
            if ('text' in content.getContentType()
                    or 'script' in content.getContentType()):
                refs = WebApi.grabRefs(content.getContent())
                urls = []
                for ref in refs:
                    try:
                        #try to prettify url
                        url = URL.prettifyURL(rootURL, ref)
                        urls.append(url)
                    except ValueError:
                        continue

                #returning extracted urls
                newContent.setContentType("linklist")
                newContent.setContent(urls)
        return newContent

    def spider(self):
        """
        spider-routine of the URL_Fuzzer
        return: None
        """
        Logger.info("Spidering URL", self.host.getURL())
        toProceed = []  #buffer for open tasks
        doneURLs = []  #deadlock protection

        #starting on website-root
        rootcontent = Content(self.host.getURL())
        rootcontent.setProcessor(URL_Fuzzer.__spiderworker__)
        toProceed.append(rootcontent)

        for i in range(0, Settings.readAttribute("recursion_depth", 0)):

            #writing buffer in queue
            for a in range(0, len(toProceed)):
                content = toProceed.pop()
                Content_Worker.queue.put(content)

            #waiting for workers to finish
            Logger.info('Processing recursion', i,
                        Content_Worker.queue.qsize(), 'task(s) to be done')
            Content_Worker.queue.join()

            #processing finished resulsts
            while not Content_Worker.done.empty():
                content = Content_Worker.done.get()
                Content_Worker.done.task_done()

                if content.getContentType() != "linklist":
                    continue

                urls = content.getContent()
                for url in urls:
                    path = url.getPath()
                    if self.host.isExternal(
                            url) or url.getURL() in doneURLs or len(path) == 0:
                        continue
                    doneURLs.append(url.getURL())
                    length = content.getSize()
                    self.host.getRootdir().appendPath(path, length)
                    newContent = Content(url)
                    newContent.setProcessor(URL_Fuzzer.__spiderworker__)
                    toProceed.append(newContent)

        #printing result
        print(self.host.getRootdir())
        Logger.info("spidering completed")

    @staticmethod
    def __fuzzworker__(content):
        """
        the function called by Content_Worker to proceed the content-Object
        attribute content: the content to proceed
        return: the proceeded content
        """

    def __scan_for_dirs__(dir):
        """
        scans for hidden dirs in the given dir and appends them to the dir
        attribute dir: the root dir for the scan
        return: the updated dir
        """

    def __scan_for_files__(dir):
        """
        scans for hidden files in the given dir and appends them to the dir
        attribute dir: the root dir for the scan
        return: the updated dir
        """

    def __scan_for_mutations__(dir):
        """
        scan for mutations of known files in the given dir and appends any hits to the given dir
        attribute dir: the root dir for the scan
        return: the updated dir
        """

    def __scan_dir__(dir):
        """
        runs all scans over a given dir recursively and appends any hits to the root-dir
        attribute dir: the root dir for the scan
        return: the updated dir
        """

    def fuzz(self):
        Logger.info("fuzzing URL", self.host.getURL())
        recursion_depth = Settings.readAttribute("recursion_depth", 0)
        for i in range(0, recursion_depth):
            Logger.info("Processing recursion", i)

        Logger.info("fuzzing completed")


def startup():
    """
    initializes the program, writes all startup options in the Settings Object
    return: None
    """

    # parsing command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'url', metavar='url', help="the victims adress", type=str, nargs='+')
    parser.add_argument(
        '-t',
        '--threads',
        help="the amount of threads to use",
        type=int,
        default=64)
    parser.add_argument(
        '-r',
        '--recursion',
        help="the maximum recursion depth",
        type=int,
        default=5)
    parser.add_argument(
        "-s", "--spider", action="store_true", help="spider the given website")
    parser.add_argument(
        "-f",
        "--fuzz",
        action="store_true",
        help="fuzz the given url to discover hidden files")
    parser.add_argument(
        "--verifyCert",
        action="store_true",
        help="verify the hosts certificate")

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

        Settings.writeAttribute("host_url", host_url)
        Settings.writeAttribute("spider", spider)
        Settings.writeAttribute("fuzz", fuzz)
        Settings.writeAttribute("verify_cert", verify_cert)
        Settings.writeAttribute("threads", threads)
        Settings.writeAttribute("recursion_depth", recursion_depth)

        #read config-file
        Settings.readConfig("config/config.ini")

        WebApi.setProtocol(
            URL(Settings.readAttribute("host_url", "")).getProto())
    except ValueError as e:
        raise e


def startWorkers(amount=4):
    """
    starts the workers
    attribute amount: the amount of workers to start
    return: None
    """

    Logger.info("Starting " + str(amount) + " threads")
    for i in range(0, amount):
        c = Content_Worker()
        c.start()
        Content_Worker.workers.append(c)
    Logger.info("Threads started")


def stopWorkers():
    """
    stops the running workers
    return: None
    """

    Logger.info("stopping workers")
    for w in Content_Worker.workers:
        Content_Worker.queue.put(TERMINATE_WORKER)
    for w in Content_Worker.workers:
        w.join()

    Logger.info("stopped workers")


def shutdown():
    """
    cleans up and stops the program
    return: None
    """

    try:
        stopWorkers()
    except:
        Logger.error("failed to stop threads!")

    Logger.info("finished scan")
    exit()


if __name__ == "__main__":
    print_banner()

    try:
        startup()
        startWorkers(Settings.readAttribute("threads", 0))
    except ValueError as e:
        Logger.error(e)
        exit()

    targetHost = Host(
        URL(Settings.readAttribute("host_url", "")),
        Dir(Settings.readAttribute("root_dir", ""), None))

    urlFuzzer = URL_Fuzzer(targetHost)

    if Settings.readAttribute("spider", False):
        urlFuzzer.spider()

    if Settings.readAttribute("fuzz", False):
        urlFuzzer.fuzz()

    shutdown()
