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

from TermTk.TTkCore.log import TTkLog
from TermTk.TTkCore.color import TTkColor
from TermTk.TTkCore.string import TTkString
from TermTk.TTkWidgets.widget import TTkWidget

class TTkImage(TTkWidget):
    __slots__ = ('_data')
    def __init__(self, *args, **kwargs):
        TTkWidget.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'TTkImage' )
        self._data = kwargs.get('data' , [] )
        if self._data:
            w = min([len(i) for i in self._data])
            h = len(self._data)
            self.resize(w//2,h//2)

    def _reduce(self, a,b,c,d):
        # quadblitter notcurses like
        l = (a,b,c,d)
        def delta(i):
            return max([v[i] for v in l]) - min([v[i] for v in l])
        deltaR = delta(0)
        deltaG = delta(1)
        deltaB = delta(2)

        def midColor(c1,c2):
            return ((c1[0]+c2[0])//2,(c1[1]+c2[1])//2,(c1[2]+c2[2])//2)

        def closer(a,b,c):
            return \
                ( (a[0]-c[0])**2 + (a[1]-c[1])**2 + (a[2]-c[2])**2 ) > \
                ( (b[0]-c[0])**2 + (b[1]-c[1])**2 + (b[2]-c[2])**2 )

        def splitReduce(i):
            s = sorted(l,key=lambda x:x[i])
            mid = (s[3][i]+s[0][i])//2
            if s[1][i] < mid:
                if s[2][i] > mid:
                    c1 = midColor(s[0],s[1])
                    c2 = midColor(s[2],s[3])
                else:
                    c1 = midColor(s[0],s[1])
                    c1 = midColor(c1,s[2])
                    c2 = s[3]
            else:
                c1 = s[0]
                c2 = midColor(s[1],s[2])
                c2 = midColor(c1,s[3])


            ch  = 0x01 if closer(c1,c2,l[0]) else 0
            ch |= 0x02 if closer(c1,c2,l[1]) else 0
            ch |= 0x04 if closer(c1,c2,l[2]) else 0
            ch |= 0x08 if closer(c1,c2,l[3]) else 0

                   # 0x00 0x01 0x02 0x03
            quad = [ ' ', '▘', '▝', '▀',
                   # 0x04 0x05 0x06 0x07
                     '▖', '▌', '▞', '▛',
                   # 0x08 0x09 0x0A 0x0B
                     '▗', '▚', '▐', '▜',
                   # 0x0C 0x0D 0x0E 0x0F
                     '▄', '▙', '▟', '█']

            return  TTkString() + \
                    (TTkColor.bg(f'#{c1[0]:02X}{c1[1]:02X}{c1[2]:02X}') + \
                     TTkColor.fg(f'#{c2[0]:02X}{c2[1]:02X}{c2[2]:02X}')) + \
                    quad[ch]

        if deltaR >= deltaG and deltaR >= deltaB:
            # Use Red as splitter
            return splitReduce(0)
        elif deltaG >= deltaB and deltaG >= deltaR:
            # Use Green as splitter
            return splitReduce(1)
        else:
            # Use Blue as splitter
            return splitReduce(2)

    @staticmethod
    def _rgb2hsl(rgb):
        r = rgb[0]/255
        g = rgb[1]/255
        b = rgb[2]/255
        cmax = max(r,g,b)
        cmin = min(r,g,b)

        lum = (cmax-cmin)/2
        if cmax == cmin:
            return 0,0,lum

        delta = cmax-cmin
        if   cmax == r:
            hue = ((g-b)/delta)%6
        elif cmax == g:
            hue = (b-r)/delta+2
        else:
            hue = (r-g)/delta+4

        sat = delta / (1 - abs(delta-1))
        hue = int(hue*60) + ( 360 if hue < 0 else 0 )
        sat = int(sat*100)
        lum = int(lum*100)

        return hue,sat,lum

    @staticmethod
    def _hsl2rgb(hsl):
        hue = hsl[0]
        sat = hsl[1] / 100
        lum = hsl[2] / 100

        c = (1-abs(2*lum-1))*sat
        x = c*(1-abs((hue/60)%2-1))
        m = lum-c/2

        if     0 <= hue < 60:
          r,g,b = c,x,0
        elif  60 <= hue < 120:
          r,g,b = x,c,0
        elif 120 <= hue < 180:
          r,g,b = 0,c,x
        elif 180 <= hue < 240:
          r,g,b = 0,x,c
        elif 240 <= hue < 300:
          r,g,b = x,0,c
        elif 300 <= hue < 360:
          r,g,b = c,0,x

        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)

        return r,g,b

    def rotHue(self, deg):
        old = self._data
        self._data = [[p for p in l ] for l in old]
        for row in self._data:
            for i,pixel in enumerate(row):
                h,s,l = self._rgb2hsl(pixel)
                h += deg
                #TTkLog.debug(f"{h=}")
                if h >= 360: h-=360
                row[i] = self._hsl2rgb((h,s,l))

    def paintEvent(self):
        img = self._data
        for y in range(0, len(img)&(~1), 2):
            for x in range(0, min(len(img[y])&(~1),len(img[y+1])&(~1)), 2):
                self._canvas.drawText( \
                        pos=(x//2,y//2), \
                        text=self._reduce(
                                    img[y][x]   , img[y][x+1]   ,
                                    img[y+1][x] , img[y+1][x+1] ))
