#!/usr/bin/env python3
# pgettext.py - a workaround for an unimplemented pgettext function
# jcj 2020-02-08, 2020-02-11

# This file assumes that _ has been injected into the builtins
# namespace by the '__main__' file.

# Explanation at https://www.php.net/manual/en/book.gettext.php,
# third posting by sasq at go2 dot pl
def pgettext(context, message):
	'''Return a context-limited translation'''
	combined = '%s\x04%s' % (context, message)   # the \x04 is magic
	result = _(combined)
	if result == combined:
		return message
	else:
		return result


