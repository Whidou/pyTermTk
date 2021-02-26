#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 Eugenio Parodi <ceccopierangiolieugenio AT googlemail DOT com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from TermTk.TTkCore.cfg import TTkCfg
from TermTk.TTkCore.log import TTkLog
from TermTk.TTkCore.helper import TTkHelper
from TermTk.TTkCore.signal import pyTTkSlot, pyTTkSignal
from TermTk.TTkCore.color import TTkColor
from TermTk.TTkWidgets.widget import *


'''
     Line Edit: |_________-___________|
     Text  "abcdefbhijklmnopqrstuvwxyz12345"
            <------------> Cursor Position
            <-->           Offset
'''
class TTkLineEdit(TTkWidget):
    __slots__ = ('_text', '_cursorPos', '_offset', '_replace', '_inputType')
    def __init__(self, *args, **kwargs):
        TTkWidget.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'TTkLineEdit' )
        self._inputType = kwargs.get('inputType' , TTkK.Input_Text )
        self._text = kwargs.get('text' , '' )
        if self._inputType & TTkK.Input_Number and\
           not self._text.isdigit(): self._text = ""
        self._offset = 0
        self._cursorPos = 0
        self._replace=False
        self.setMaximumHeight(1)
        self.setMinimumSize(10,1)
        self.setFocusPolicy(TTkK.ClickFocus + TTkK.TabFocus)

    def _pushCursor(self):
        TTkHelper.moveCursor(self,self._cursorPos-self._offset,0)
        if self._replace:
            TTkHelper.showCursor(TTkK.Cursor_Blinking_Block)
        else:
            TTkHelper.showCursor(TTkK.Cursor_Blinking_Bar)
        self.update()

    def paintEvent(self):
        if self.hasFocus():
            color = TTkCfg.theme.lineEditTextColorFocus
        else:
            color = TTkCfg.theme.lineEditTextColor
        w = self.width()
        if self._inputType & TTkK.Input_Password:
            text = ("*"*(len(self._text)))[self._offset:]
        else:
            text = self._text[self._offset:]
        text = text[:w].ljust(w)
        self._canvas.drawText(pos=(0,0), text=text, color=color)

    def mousePressEvent(self, evt):
        x,y = evt.x, evt.y
        txtPos = x+self._offset
        if txtPos > len(self._text):
            txtPos = len(self._text)
        self._cursorPos = txtPos
        self._pushCursor()


    def keyEvent(self, evt):
        w = self.width()
        if evt.type == TTkK.SpecialKey:
            if evt.key == TTkK.Key_Up: pass
            elif evt.key == TTkK.Key_Down: pass
            elif evt.key == TTkK.Key_Left:
                if self._cursorPos > 0:
                    self._cursorPos -= 1
            elif evt.key == TTkK.Key_Right:
                if self._cursorPos < len(self._text):
                    self._cursorPos += 1
            elif evt.key == TTkK.Key_End:
                self._cursorPos = len(self._text)
            elif evt.key == TTkK.Key_Home:
                self._cursorPos = 0
            elif evt.key == TTkK.Key_Insert:
                self._replace = not self._replace
            elif evt.key == TTkK.Key_Delete:
                self._text = self._text[:self._cursorPos] + self._text[self._cursorPos+1:]
            elif evt.key == TTkK.Key_Backspace:
                if self._cursorPos > 0:
                   self._text = self._text[:self._cursorPos-1] + self._text[self._cursorPos:]
                   self._cursorPos -= 1

            # Scroll to the right if reached the edge
            if self._cursorPos - self._offset > w:
                self._offset = self._cursorPos - w
            # Scroll to the right if reached the edge
            elif self._cursorPos - self._offset < 0:
                self._offset = self._cursorPos
            self._pushCursor()
        else:
            if self._inputType & TTkK.Input_Number and \
               not evt.key.isdigit():
                return
            text = self._text
            pre = text[:self._cursorPos]
            if self._replace:
                post = text[self._cursorPos+1:]
            else:
                post = text[self._cursorPos:]

            text = pre + evt.key + post
            self._text = text
            self._cursorPos += 1
            # Scroll to the right if reached the edge
            if self._cursorPos - self._offset > w:
                self._offset += 1
            self._pushCursor()

    def focusInEvent(self):
        self._pushCursor()

    def focusOutEvent(self):
        TTkHelper.hideCursor()
        self.update()