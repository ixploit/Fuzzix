"""
providing high-level functions for Fuzzix.py
"""

from coloredlogger import ColoredLogger
LOGGER = ColoredLogger(name="MAIN")


def print_banner():
    """
    prints the applications' banner
    """
    banner = """
                          .-') _    .-') _         ) (`-.      
                         (  OO) )  (  OO) )         ( OO ).    
   ,------.,--. ,--.   ,(_)----. ,(_)----.   ,-.-')(_/.  \_)-. 
('-| _.---'|  | |  |   |       | |       |   |  |OO)\  `.'  /  
(OO|(_\    |  | | .-') '--.   /  '--.   /    |  |  \ \     /\  
/  |  '--. |  |_|( OO )(_/   /   (_/   /     |  |(_/  \   \ |  
\_)|  .--' |  | | `-' / /   /___  /   /___  ,|  |_.' .'    \_) 
  \|  |_) ('  '-'(_.-' |        ||        |(_|  |   /  .'.  \  
   `--'     `-----'    `--------'`--------'  `--'  '--'   '--' 


 by @cybertschunk   cybertschunk@mailbox.org
 """
    print(banner)