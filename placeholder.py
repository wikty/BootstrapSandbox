import re

regexp = {}

regexp['extend'] = re.compile(
    r'''
    # one file have only one extend mark, and must be in file's header
    \A(?:^\s*#+.*)+                     # spaces and comments(#) before extend mark
    {%\s*                               # extend left delimiter
    extend\s+                           # extend identifier
    (?P<quote>["']?)                    # quote
    (?P<filename>[-a-zA-Z0-9_.]+)       # filename
    (?(quote)(?P=quote)|\s*))           # quote
    \s*%}                               # extend right delimiter
    ''',
    re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE)

regexp['block'] = re.compile(
    r'''
    (?P<blockstart>{%\s*                # block start-left delimiter
    block\s+                            # block start identifier
    (?P<blockname>[-a-zA-Z0-9_.]+)      # block name
    \s*%})                              # block start-right delimiter
    
    (?P<subcontent>.*?)                  # block content
    
    (?P<blockend>{%\s*                  # block end-left delimiter
    endblock                            # block end identifier
    \s*%})                              # block end-right delimiter
    ''', 
    re.IGNORECASE | re.UNICODE | re.DOTALL | re.VERBOSE)

regexp['blockdelimiter'] = re.compile(
    r'''
    (
    (?P<blockstart>{%\s*                # block start-left delimiter
    block\s+                            # block start identifier
    (?P<blockname>[-a-zA-Z0-9_.]+)      # block name
    \s*%})                              # block start-right delimiter
    |
    (?P<blockend>{%\s*                  # block end-left delimiter
    endblock                            # block end identifier
    \s*%})
    )
    ''',
    re.IGNORECASE | re.UNICODE | re.DOTALL | re.VERBOSE)
