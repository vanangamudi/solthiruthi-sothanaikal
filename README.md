# tace16-utf8-converter

## Tamil Unicode (From Wikipedia)
Tamil is a Unicode block containing characters for the Tamil, Badaga, and Saurashtra languages of Tamil Nadu India, Sri Lanka, Singapore, and Malaysia. In its original incarnation, the code points U+0B02..U+0BCD were a direct copy of the Tamil characters A2-ED from the 1988 ISCII standard. The Devanagari, Bengali, Gurmukhi, Gujarati, Oriya, Telugu, Kannada, and Malayalam blocks were similarly all based on their ISCII encodings.

## TACE16 (From Wikipedia)
Tamil All Character Encoding (TACE16) is a 16-bit Unicode-based character encoding scheme for Tamil language.

TACE16 is better suited for the tamil grammar and slightly differs from UTF-16 encoding. I couldn't find any codec helpers for TACE16 so I had planned to write one a while now. Luckily I was experimenting with [tamil name generation with neural networks](https://github.com/vanangamudi/tamil-name-gen/tree/master) last week and these projects acted like a symboiotic motivation for me to complete this one. This is still work in progress and not yet include converters for other unicode encodings like UTF-32 and UTF-16. I chose to do UTF-8 first because I have the dataset in that form.

