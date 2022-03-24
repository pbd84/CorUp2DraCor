# CorUp2DraCor (https://pbd84.github.io/CorUp2DraCor/)

CorUp2DraCor ergibt ausgeschrieben sowas wie: “NDR Coronavirus-Update Podcast Transkripte PDF zu Drama Corpus Project TEI”. Die als PDFs vorliegenden Transkripte  werden zunächst durch das Skript “ndr2CorPo.py” in ein Zwischenformat (JSON) überführt. Das JSON-Datenmodell wurde im Laufe des Seminars “Die Pandemie in Sprache und Text - Corona-Podcasts & Co.” zur gemeinsamen Basis für Auswertungen entwickelt. Mit “CorPo2DraCor.py” findet schließlich die Konversion in das DraCor-TEI-Format statt.

(Als Grundlage für CorUp2DraCor.py diente ein für das Seminar von Moritz Eßer (und dessen Gruppe) geschriebenes Skript, das von mir weitgehend modifiziert wurde: https://github.com/Zadest/PodcastNLP/blob/dev-moritz/pdftotext_ndr.py)
