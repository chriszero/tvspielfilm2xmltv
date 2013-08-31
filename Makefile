#
# Makefile for tvspielfilm2xmltv
#

GRABBER = tvspielfilm2xmltv

DESTDIR ?=
PREFIX  ?= /usr/local
MANDIR   = $(PREFIX)/share/man
BINDIR   = $(PREFIX)/bin
APPDIR   = $(PREFIX)/share/$(GRABBER)

.PHONY: install

all:
	@true

install:
# Install the progam files
	@install -D tvspielfilm2xmltv.py $(DESTDIR)/$(APPDIR)/tvspielfilm2xmltv.py
	@install -d $(DESTDIR)/$(APPDIR)/tvsp2xmltv
	@install -D tvsp2xmltv/*.py $(DESTDIR)/$(APPDIR)/tvsp2xmltv
# Install the config
	@install -d $(DESTDIR)/etc/$(GRABBER)
	@install -b tvspielfilm2xmltv.ini $(DESTDIR)/etc/$(GRABBER)/tvspielfilm2xmltv.ini
# Install the man page
	@install -d $(DESTDIR)/$(MANDIR)/man1/
	@gzip -c9 $(GRABBER).1 > $(DESTDIR)/$(MANDIR)/man1/$(GRABBER).1.gz
# create the app link
	@install -d $(DESTDIR)/$(BINDIR)
	@rm -f $(DESTDIR)/$(BINDIR)/$(GRABBER)
	@ln -s $(DESTDIR)/$(APPDIR)/tvspielfilm2xmltv.py $(DESTDIR)/$(BINDIR)/$(GRABBER)
# Install the Grabber API
	@install -d $(DESTDIR)/var/lib/epgsources/$(GRABBER)-img
#
# ugo+rw because may different user work with this file
#
	@chmod ugo+w $(DESTDIR)/var/lib/epgsources
	@chmod ugo+w $(DESTDIR)/var/lib/epgsources/$(GRABBER)-img
