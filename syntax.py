import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def format(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages

STYLES = {
    'keyword': format([200, 120, 50], 'bold'),
    'if_keyword': format([247, 170, 82], 'bold'),
    'or_keyword': format([73, 122, 214], 'bold'),
    'import_keyword': format([217, 79, 219]),
    'operator': format([246, 250, 35]),
    'brace': format('darkGray'),
    'defclass': format([68, 178, 242], 'bold'),
    'string': format([20, 110, 100]),
    'string2': format([30, 120, 110]),
    'comment': format([9, 189, 54]),
    'self': format([223, 145, 235], 'italic'),
    'numbers': format([100, 150, 190]),
}


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords


    keywords = [
        'assert', 'break', 'class', 'continue', 'def',
        'del', 'except', 'exec', 'finally',
        'from', 'global', 'import', 
        'lambda', 'pass', 'print',
        'raise', 'return', 'yield',
        'None', 'True', 'False', 
    ]
    if_keywords = [
        'if', 'elif', 'else', 'is', 'for', 'while',
        'try', 'except',
    ]
    or_keywords = [
        'in', 'and', 'or', 'not',
    ]
    import_keywords = [
        'import', 'from',
    ]
    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PythonHighlighter.keywords]
        rules += [(r'\b%s\b' % iw, 0, STYLES['if_keyword'])
                  for iw in PythonHighlighter.if_keywords]
        rules += [(r'\b%s\b' % ow, 0, STYLES['or_keyword'])
                  for ow in PythonHighlighter.or_keywords]
        rules += [(r'\b%s\b' % impw, 0, STYLES['import_keyword'])
                  for impw in PythonHighlighter.import_keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

class XMLHighlighter(QSyntaxHighlighter):
    '''
    Class for highlighting xml text inherited from QSyntaxHighlighter
    reference:
        http://www.yasinuludag.com/blog/?p=49
    '''

    def __init__(self, parent=None):

        super(XMLHighlighter, self).__init__(parent)

        self.highlightingRules = []

        xmlElementFormat = QTextCharFormat()
        xmlElementFormat.setForeground(QColor("#3d9cf5"))  # dark magenta
        # self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=[\s/>])"), xmlElementFormat))
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=[\/>])"), xmlElementFormat))
        xmlAttributeFormat = QTextCharFormat()
        xmlAttributeFormat.setFontItalic(True)
        xmlAttributeFormat.setForeground(QColor("#11e4f7"))  # magenta
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\=)"), xmlAttributeFormat))
        self.highlightingRules.append((QRegExp("="), xmlAttributeFormat))

        self.valueFormat = QTextCharFormat()
        self.valueFormat.setForeground(QColor("#e35e00"))  # orange
        self.valueStartExpression = QRegExp("\"")
        self.valueEndExpression = QRegExp("\"(?=[\s></])")
        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(QColor("#228030"))  # green
        self.highlightingRules.append((QRegExp("<!--[^\n]*-->"), singleLineCommentFormat))

        textFormat = QTextCharFormat()
        textFormat.setForeground(QColor("#ebf7e9"))  # light green
        # (?<=...)  - lookbehind is not supported
        self.highlightingRules.append((QRegExp(">(.+)(?=</)"), textFormat))

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#686968"))  # grey
        keywordFormat.setFontWeight(QFont.Bold)
        keywordPatterns = ["<\\?", "\\b?xml\\b", "/>", ">", "<", "</", "\\b?\\>"]
        self.highlightingRules += [(QRegExp(pattern), keywordFormat)
                                   for pattern in keywordPatterns]

    # VIRTUAL FUNCTION WE OVERRIDE THAT DOES ALL THE COLLORING
    def highlightBlock(self, text):
        # for every pattern
        for pattern, format in self.highlightingRules:
            # Create a regular expression from the retrieved pattern
            expression = QRegExp(pattern)
            # Check what index that expression occurs at with the ENTIRE text
            index = expression.indexIn(text)
            # While the index is greater than 0
            while index >= 0:
                # Get the length of how long the expression is true, set the format from the start to the length with the text format
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                # Set index to where the expression ends in the text
                index = expression.indexIn(text, index + length)

                # HANDLE QUOTATION MARKS NOW.. WE WANT TO START WITH " AND END WITH ".. A THIRD " SHOULD NOT CAUSE THE WORDS INBETWEEN SECOND AND THIRD TO BE COLORED
        self.setCurrentBlockState(0)
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.valueStartExpression.indexIn(text)
        while startIndex >= 0:
            endIndex = self.valueEndExpression.indexIn(text, startIndex)
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.valueEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.valueFormat)
            startIndex = self.valueStartExpression.indexIn(text, startIndex + commentLength);


