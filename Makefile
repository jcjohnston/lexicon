# i18n and l10n makefile for lexitron
# jcj 2020-02-11, 2020-05-12, 2020-06-17, 2020-06-19, 2021-03-25

ifeq ($(OS),Windows_NT)
	PLATFORM=Windows
else
	PLATFORM=$(shell uname)
endif

DOMAIN=lexitron
LANGUAGES=en fr
LOCALES=$(HOME)/locales
TEMPLATE=$(LOCALES)/$(DOMAIN).pot
MYLIB=my
PYTHON_VERSION=3.6
ifeq ($(PLATFORM),Darwin)
	LOCAL_LIB=$(HOME)/Library/Python/$(PYTHON_VERSION)/lib/python/site-packages/$(MYLIB)
else
	LOCAL_LIB=$(HOME)/.local/lib/python$(PYTHON_VERSION)/site-packages/$(MYLIB)
endif
LOCAL_IMPORTS=$(LOCAL_LIB)/error.py $(LOCAL_LIB)/textutils.py
SOURCES=*.py $(LOCAL_IMPORTS)

usage:
	@echo 'Usage: make xgettext|msginit|msgmerge|msgfmt'

xgettext:
	xgettext --from-code=utf-8 --keyword=__:1c,2 \
		 -o $(TEMPLATE) $(SOURCES)

msginit:
	$(foreach LANGUAGE, $(LANGUAGES), \
	    msginit -l $(LANGUAGE) -i $(TEMPLATE) \
		-o $(LOCALES)/$(LANGUAGE)/LC_MESSAGES/$(DOMAIN).po;)

msgmerge:
	$(foreach LANGUAGE, $(LANGUAGES), \
	    msgmerge --update \
	        $(LOCALES)/$(LANGUAGE)/LC_MESSAGES/$(DOMAIN).po $(TEMPLATE);)

msgfmt:
	$(foreach LANGUAGE, $(LANGUAGES), \
	    msgfmt -o $(LOCALES)/$(LANGUAGE)/LC_MESSAGES/$(DOMAIN).mo \
	        $(LOCALES)/$(LANGUAGE)/LC_MESSAGES/$(DOMAIN).po;)
