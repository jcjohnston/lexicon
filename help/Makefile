# i18n and l10n makefile for lexitron documentation
# jcj 2020-02-11, 2020-05-12, 2020-06-16

DOMAIN=lexitron-documentation
LOCALES=/home/jason/locales
TEMPLATE=$(LOCALES)/$(DOMAIN).pot
PYTHON_VERSION=python3.6
LOCAL_LIB=/home/jason/.local/lib/$(PYTHON_VERSION)/site-packages/my
LOCAL_IMPORTS=$(LOCAL_LIB)/error.py $(LOCAL_LIB)/textutils.py
SOURCES=lexDoc.py $(LOCAL_IMPORTS)
LANGUAGES=en fr

help:
	@echo 'Type: make xgettext|msginit|msgmerge|msgfmt'

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
