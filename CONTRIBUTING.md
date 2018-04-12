# Contribution guidelines
*english version coming soon!*

Hallo lieber Entwickler, 
vielen Dank, dass du dich in unser Projekt einbringen möchtest. Das freut uns sehr! Diese Anleitung soll dir dabei helfen. Bevor du anfängst in die Tasten zu hauen, lese sie dir bitte einmal komplett durch. Ich hab auch versucht, mich kurzzufassen, versprochen! ;-) 

## Code of conduct
Für dieses Projekt gibt es einen [Code of conduct](https://github.com/ixploit/ixfuzz/blob/master/CODE_OF_CONDUCT.md), der für alle Entwickler verpflichtend ist. Bitte lese ihn dir vorab einmal durch. Solltest du einmal erleben, dass andere Entwickler gegen diese Richtlinien verstoßen, wende dich bitte umgehend an @cybertschunk, bzw. cybertschunk@mailbox.org

## Wie entwickeln wir?
ixfuzz wird in [Python3](https://www.python.org/) programmiert. Als Entwicklungsumgebung nutzen wir [Visual Studio Code](https://code.visualstudio.com/). Entsprechend liegen diesem Repository bereits Konfigurationsdateien für diese Umgebung bei. Wir empfehlen dir daher, ebenfalls auf VSC zurückzugreifen. Das Programm ist für nahezu alle Plattformen (Linux, Windows, Mac OS) verfügbar. 

## Welche Richtlinien sollte ich beachten?

 1. Pull Requests müssen sich immer auf einen (oder mehrere) offene Issues beziehen. Entdeckst du einen Fehler und möchtest diesen schließen, öffne also einfach vorab einen entsprechenden Issue und gebe an, dass du diesen bearbeiten möchtest.
 2. Der oder die Issues, auf die sich der Pull-Request bezieht, müssen im Pull-Request zur besseren Übersicht referenziert werden.
 3. Pull-Requests werden bitte immer gegen den Master-Branch gestellt.
 4. Sprache dieses Projekts ist im Allgemeinen Englisch. 

## Wie programmiere ich am besten?
Achte auf einen aussagekräftigen Programmcode. Variablen, Funktionen und Klassen sollten aussagekräftige Namen tragen. Auch ist es Ziel der beteiligten Entwickler, jeder Funktion und jeder Klasse einen aussagekräftigen Kommentar über deren Funktion beizulegen. 
Dieser Kommentar sollte **für Funktion** eine **kurze Erklärung der bewältigten Aufgabe**, eine Angabe über **eventuelle Exceptions**, eine kurze Info über den **Rückgabewert** (inklusive Typ) sowie die **erwarteten Parameter** (ebenfalls inklusive Typ) enthalten. Das kann wie folgt aussehen:

    def  __init__(self, url):
    """
    
    initializes the object with a given URL
    
    attribute url: the url the object is meant to store
    
    return: None
    
    raises: ValueError if no valid URL is passed
    
    """

Für Klassen genügt eine kurze Erklärung des Aufgabenfeldes.
## Was sonst noch?
Bitte gib mir Feedback! Einfach kontaktieren @cybertschunk oder per Mail (cybertschunk@mailbox.org). Das hier ist mein erstes Open-Source-Projekt und sicher mache ich vieles falsch. Daher bin ich dankbar für jede Anregung. Auch Fragen kannst du mir gerne stellen. Beachte jedoch vorab bitte, dass aktuell hier noch vieles im entstehen ist.  

