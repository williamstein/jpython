# vim:fileencoding=utf-8
# License: BSD Copyright: 2015, Kovid Goyal <kovid at kovidgoyal.net>

from gettext import gettext as _, ngettext, install

g = require('../tools/gettext.js')

def gettext(code):
    ans = {}
    g.gettext(ans, code, '<test>')
    return ans

def test_string(code, *args):
    catalog = gettext(code)
    assrt.equal(len(catalog), len(args))
    for msgid, q in zip(Object.keys(catalog), args):
        assrt.equal(g.entry_to_string(msgid, catalog[msgid]), q)

test_string('a = _("one")', '#: <test>:1\nmsgid "one"\nmsgstr ""')
test_string('a = _("one")\nb = gettext("one")', '#: <test>:1\n#: <test>:2\nmsgid "one"\nmsgstr ""')
test_string('''a = _("""one
two""")''', '#: <test>:1\nmsgid "one\\ntwo"\nmsgstr ""')
test_string('a = _("{}one")', '#: <test>:1\n#, python-brace-format\nmsgid "{}one"\nmsgstr ""')
test_string('a = _("{one}")', '#: <test>:1\n#, python-brace-format\nmsgid "{one}"\nmsgstr ""')
test_string('ngettext("one", "two", 1)', '#: <test>:1\nmsgid "one"\nmsgid_plural "two"\nmsgstr[0] ""\nmsgstr[1] ""')
test_string('''_('o"ne')''', '#: <test>:1\nmsgid "o\\"ne"\nmsgstr ""')

m = require('../tools/msgfmt.js')
catalog = m.parse(r'''
msgid ""
msgstr ""
"Language: en\n"
"Plural-Forms: nplurals=2; \n"

#, fuzzy
msgid "one\n"
"continued"
msgstr "ON"
"E"

msgid "two"
msgid_plural "three"
msgstr[0] "a"
"bc"
msgstr[1] "def"

msgid "test \"quote\" escape"
msgstr "good"
''')

assrt.equal(2, catalog['nplurals'])
assrt.equal('en', catalog['language'])
assrt.equal(catalog['entries'].length, 3)
item = catalog['entries'][0]
assrt.equal(item['msgid'], 'one\ncontinued')
assrt.deepEqual(item['msgstr'], v"['ONE']")
assrt.ok(item['fuzzy'], 'item not fuzzy')
item = catalog['entries'][1]
assrt.equal(item['msgid'], 'two')
assrt.deepEqual(item['msgstr'], v"['abc', 'def']")
assrt.ok(not item['fuzzy'], 'item not fuzzy')
item = catalog['entries'][2]
assrt.equal(item['msgid'], 'test "quote" escape')
assrt.deepEqual(item['msgstr'], v"['good']")

install({'entries': {
    'one':['ONE'],
    'two':['1', '2'],
}})

assrt.equal(_('one'), 'ONE')
assrt.equal(ngettext('two', 'xxx', 1), '1')
assrt.equal(ngettext('two', 'xxx', 100), '2')
