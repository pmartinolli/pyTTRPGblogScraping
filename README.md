# pyTTRPGblogScraping

Python tools for web scraping, analyzing, and preserving tabletop role-playing games blogs

Tools : 
- `pyURLfromObsidianMD.py` : turn an Obsidian.md vault of markdown files into a list of URLs to feed `pyTTRPGblogCitationWS.py`
- `pyTTRPGblogCitationWS.py` : web scrap TTRPG (TTRPG) blogs and figure it out who cites who from their homepage cited URLs
- `pyTTRPGblogCitationIterationX.py` : create a list of URLs to feed `pyTTRPGblogCitationWS.py` from the Cited URLs from the last iteration (ideally when a big turn of iterations is finished) 
- `pyTTRPGblogCleaner.py` : clean the output file of `pyTTRPGblogCitationWS.py`

Project is discussed [here in French](https://jdr.hypotheses.org/1998)