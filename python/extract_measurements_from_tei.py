#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# Author: Paolo Monella
#
# This script is provided with a MIT License:
#
# The MIT License (MIT)
#
# Copyright © 2022 <copyright holders>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files
# (the “Software”), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from lxml import etree
import re

myInputFileName = 'xml/02.xml'
myOutputFileName = 'xml/out-02.xml'
quiet = True

ns = {
    # For elements without prefix:
    None: 'http://www.tei-c.org/ns/1.0',
    # for TEI XML:
    't': 'http://www.tei-c.org/ns/1.0',
    # for attributes like xml:id:
    'xml': 'http://www.w3.org/XML/1998/namespace',
    # for (X)HTML output
    'h': 'http://www.w3.org/1999/xhtml',
    # for bibtexml, ouput of Jabref
    'b': 'http://bibtexml.sf.net/'}

interestingCellTypes = [
    'quantità',
    'costo_unitario',
    'costo_totale'
]

'''
Abbreviations:
            o. = oncia
            £. = lire / libbre
            (convertito in lb. quando indica le libbre da MG)
            s. = soldi
            d. = denari
            £. 42 s. 17 d. = 42 lire, 17 soldi, 0 denari

abbr = {
            'o.': 'oncia',
            '£.': 'lira',
            's.': 'solidus',
            'd.': 'denarius',
}
            '''


tree = etree.parse(myInputFileName)


def myBody(tree):
    myBodyElement = tree.find('.//t:body', ns)
    return myBodyElement


def returnAllCellsOfAType(myFilePath, interestingCellType):
    body = myBody(tree)
    myCellElements = body.findall('.//t:cell[@ana="%s"]'
                                  % (interestingCellType), ns)
    return myCellElements


def testIfCellsAreReturned():
    for interestingCellType in interestingCellTypes:
        myCells = returnAllCellsOfAType(myInputFileName, interestingCellType)
        print('\n\n---\nType %s: %d cells'
              % (interestingCellType, len(myCells)))
        for myCell in myCells:
            t = ''.join(myCell.itertext()).replace('\n', '')
            print(t)


def splitByUnit(myText, myUnitAbbr):
    ''' Input text and a unit abbreviation, that can be e.g. '£.',
        and return a dictionary with keys
        {previous, number, unit, trailing},
        explained below in the function'''
    myDict = {}
    m = re.match('(.*?)(%s)(\\s?)(\\d+)(.*)' % (myUnitAbbr), myText)
    if not m:
        myDict['match'] = False
    if m:
        myDict['match'] = True
        # g0_whole_text = m.group(0)  # useless
        myDict['previous'] = m.group(1)  # Previous text
        # g2_unit = m.group(2)  # useless
        # g3_space = m.group(3) # Useless
        myDict['number'] = m.group(4)
        myDict['trailing'] = m.group(5)
        if False:
            print('\n\nWhole text: «{}»'
                  '\nPrevious text: «{}»'
                  '\nunit: «{}»'
                  # '\nspace: «{}»'
                  '\nnumber: «{}»'
                  '\ntrailing text: «{}»'.format(
                      myText,
                      myDict['previous'],
                      myUnitAbbr,
                      myDict['number'],
                      myDict['trailing'],
                  ))
    return myDict


def markupCell(myCell, interestingCellTypes):

    # liraFound = solidusFound = denariusFound = False
    liraFound = solidusFound = False

    myText = myCell.text

    myUnitAbbr = '£.'
    myDict = splitByUnit(myText, myUnitAbbr)
    if myDict['match']:
        liraFound = True
        myCell.text = myDict['previous']  # Set previous text as cell text
        # <measure quantity="15" type="currency" unit="lira">£. 15</measure>
        liraElem = etree.SubElement(myCell, '{%s}measure' % ns['t'])
        liraElem.set('quantity', myDict['number'])
        liraElem.set('type', 'currency')
        liraElem.set('unit', 'lira')
        liraElem.text = ' '.join([myUnitAbbr, myDict['number']])
        liraElem.tail = myDict['trailing']
        myText = myDict['trailing']

    myUnitAbbr = 's.'
    myDict = splitByUnit(myText, myUnitAbbr)
    if myDict['match']:
        solidusFound = True
        if liraFound:
            liraElem.tail = myDict['previous']  # Write it after lira<measure>
        else:
            myCell.text = myDict['previous']  # Set previous text as cell text
        # <measure quantity="10" type="currency" unit="solidus">s. 10</measure>
        solidusElem = etree.SubElement(myCell, '{%s}measure' % ns['t'])
        solidusElem.set('quantity', myDict['number'])
        solidusElem.set('type', 'currency')
        solidusElem.set('unit', 'solidus')
        solidusElem.text = ' '.join([myUnitAbbr, myDict['number']])
        solidusElem.tail = myDict['trailing']
        myText = myDict['trailing']

    myUnitAbbr = 'd.'
    myDict = splitByUnit(myText, myUnitAbbr)
    if myDict['match']:
        # denariusFound = True
        if solidusFound:
            solidusElem.tail = myDict['previous']  # Write after lira <measure>
        elif liraFound and not solidusFound:
            liraElem.tail = myDict['previous']  # Write it after lira<measure>
        elif not liraFound and not solidusFound:
            myCell.text = myDict['previous']  # Set previous text as cell text
        # <measure quantity="4" type="currency" unit="denarius">d. 4</measure>
        denariusElem = etree.SubElement(myCell, '{%s}measure' % ns['t'])
        denariusElem.set('quantity', myDict['number'])
        denariusElem.set('type', 'currency')
        denariusElem.set('unit', 'denarius')
        denariusElem.text = ' '.join([myUnitAbbr, myDict['number']])
        denariusElem.tail = myDict['trailing']
        myText = myDict['trailing']

    return(myCell)


def processCells():
    for interestingCellType in interestingCellTypes:
        myCells = returnAllCellsOfAType(myInputFileName, interestingCellType)
        print('---\nType «%s»: %d cells'
              % (interestingCellType, len(myCells)))
        for myCell in myCells:
            myCellIterText = ''.join(myCell.itertext()).replace('\n', '')
            rowAttributes = myCell.getparent().attrib
            # If <cell> has children elements, pass
            if len(myCell) > 0:
                if not quiet:
                    print('Skipping the following cell because it '
                          'has children elements:'
                          '\n\tParent row attributes: {}'
                          '\n\tCell @ana: {}'
                          '\n\tText «{}»'.format(
                              rowAttributes, interestingCellType,
                              myCellIterText))
            # If <cell> has no children elements and no text at all, pass
            elif len(myCell) == 0 and myCellIterText == '':
                if not quiet:
                    print('Skipping the following cell because it '
                          'is completely empty:'
                          '\n\tParent row attributes: {}'
                          '\n\tCell @ana: {}'
                          '\n\tText «{}»'.format(
                              rowAttributes, interestingCellType,
                              myCellIterText))
            else:
                markupCell(myCell, interestingCellTypes)


processCells()
tree.write(myOutputFileName, encoding='UTF-8', method='xml',
           pretty_print=True, xml_declaration=True)
