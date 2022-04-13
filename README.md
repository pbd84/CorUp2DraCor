# CorUp2DraCor (https://pbd84.github.io/CorUp2DraCor/)

CorUp2DraCor ergibt ausgeschrieben sowas wie: **“NDR Coronavirus-Update Podcast Transkripte PDF zu Drama Corpus Project TEI”**. 

Die als PDFs vorliegenden [Transkripte](https://www.ndr.de/nachrichten/info/Coronavirus-Update-Die-Podcast-Folgen-als-Skript,podcastcoronavirus102.html) werden zunächst durch das Skript “ndr2CorPo.py” in ein Zwischenformat (JSON) überführt. Das JSON-Datenmodell wurde im Laufe des Seminars [“Die Pandemie in Sprache und Text - Corona-Podcasts & Co.”](https://lehre.idh.uni-koeln.de/lehrveranstaltungen/sosem21/die-pandemie-in-sprache-und-text-corona-podcasts-und-co/) zur gemeinsamen Basis für Auswertungen entwickelt. Mit “CorPo2DraCor.py” findet schließlich die Konversion in das [DraCor](https://dracor.org/)-TEI-Format statt.

---
“namespaces_fix.xsl”: Bereitet die Daten für https://github.com/quadrama/DramaNLP auf. (s. [Issue1](https://github.com/pbd84/CorUp2DraCor/issues/1))

---
Als Grundlage für CorUp2DraCor.py diente ein für das Seminar von [Moritz Eßer](https://github.com/Zadest) und [Tessa Johnsen](https://github.com/tessajo) geschriebenes Skript, das von mir weitgehend modifiziert wurde: https://github.com/Zadest/PodcastNLP/blob/dev-moritz/pdftotext_ndr.py - für ein schnelles Herunterladen aller Transkripte bietet sich dabei übrigens https://github.com/Zadest/PodcastNLP/blob/dev-moritz/dataCollectorNDR.py an.
