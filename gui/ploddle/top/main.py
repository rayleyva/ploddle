#!/usr/bin/env python

import requests
import threading
import time

import wx
import wx.grid
import wx.calendar

#import  wx.lib.mixins.grid  as  mixins
#print wx.version()
#import os; print "pid:", os.getpid(); raw_input("Press Enter...")
#---------------------------------------------------------------------------


class Col(object):
    def __init__(self, name, active=True, type="text", filter=None):
        self.name = name
        self.active = active
        self.type = type
        self.filter = filter

cols = [
    Col(name="timestamp", type="datetime"),
    Col(name="hostname"),
    Col(name="severity"),
    Col(name="daemon"),
    Col(name="message"),
]

class LogEntryTable(wx.grid.PyGridTableBase):
    def __init__(self, grid):
        wx.grid.PyGridTableBase.__init__(self)
        self.grid = grid
        self.data = []
        self.filters = {
            "page": -1,
        }

        self.thread = threading.Thread(target=self.UpdateLoop)
        self.thread.setDaemon(True)
        self.thread.start()

    def UpdateLoop(self):
        while True:
            self._update(append=True)
            wx.CallAfter(self.ResetView)
            time.sleep(3)

    def UpdateData(self):
        if "since" in self.filters:
            del self.filters["since"]
        self._update(append=False)

    def _update(self, append):
        r = requests.get("http://localhost:5140/api/messages.json", params=self.filters)
        print "fetched update from", r.url

        if append:
            self.data.extend(r.json()["messages"])
        else:
            self.data = r.json()["messages"]

        if self.data:
            self.filters["since"] = self.data[-1]["timestamp"]

    def OnToggleCol(self, evt):
        for col in cols:
            if col.name.title() == evt.EventObject.GetLabel():
                col.active = evt.EventObject.GetValue()
                print "Setting", col.name, "to", col.active

    def GetGrid(self):
        return self.grid

    def GetNumberRows(self):
        """Return the number of rows in the grid"""
        return len(self.data)

    def GetNumberCols(self):
        """Return the number of columns in the grid"""
        return len([c for c in cols if c.active])

    def IsEmptyCell(self, row, col):
        """Return True if the cell is empty"""
        return False

    def GetTypeName(self, row, col):
        """Return the name of the self.data type of the value in the cell"""
        return None

    def GetValue(self, row, col):
        """Return the value of a cell"""
        return self.data[row].get([c for c in cols if c.active][col].name, "")

    def SetValue(self, row, col, value):
        """Set the value of a cell"""
        pass

    def GetRowLabelValue(self, row):
        return row

    def GetColLabelValue(self, col):
        return [c for c in cols if c.active][col].name.title()

    def GetAttr(self, row, col, someExtraParameter ):
        attr = wx.grid.GridCellAttr()
        #attr.SetTextColour(wx.BLACK)
        if self.data[row]["severity"] <= 3:
            attr.SetBackgroundColour(wx.RED)
        #attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        return attr

    def ResetView(self):
            """Trim/extend the control's rows and update all values"""
            self.GetGrid().BeginBatch()
            for current, new, delmsg, addmsg in [
                    (self.grid.GetNumberRows(), self.GetNumberRows(), wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
                    (self.grid.GetNumberCols(), self.GetNumberCols(), wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
            ]:
                    if new < current:
                            msg = wx.grid.GridTableMessage(
                                    self,
                                    delmsg,
                                    new,    # position
                                    current-new,
                            )
                            self.GetGrid().ProcessTableMessage(msg)
                    elif new > current:
                            msg = wx.grid.GridTableMessage(
                                    self,
                                    addmsg,
                                    new-current
                            )
                            self.GetGrid().ProcessTableMessage(msg)
            self.UpdateValues()
            self.GetGrid().EndBatch()

            # The scroll bars aren't resized (at least on windows)
            # Jiggling the size of the window rescales the scrollbars
            grid = self.GetGrid()
            h,w = grid.GetSize()
            grid.SetSize((h+1, w))
            grid.SetSize((h, w))
            grid.ForceRefresh()

    def UpdateValues( self ):
        """Update all displayed values"""
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetGrid().ProcessTableMessage(msg)

class LogEntryGrid(wx.grid.Grid):
    def __init__(self, parent, log):
        wx.grid.Grid.__init__(self, parent, -1)
        self.log = log
        self.moveTo = None
        self.table = LogEntryTable(self)
        self.SetTable(self.table)
        #self.CreateGrid(25, 25)#, wx.grid.Grid.SelectRows)
        #self.EnableEditing(False)

        self.setup()

        #wrapper = wx.grid.GridCellAutoWrapStringRenderer()
        #for n, row in enumerate(data):
        #    if "severity" in row:
        #        if row["severity"] in self.severity:
        #            self.SetRowAttr(n, self.severity[row["severity"]])
        #    for x, col in enumerate(cols):
        #        if col == "message":
        #            self.SetCellRenderer(n, x, wrapper)
        #
        #        self.SetCellValue(n, x, unicode(row.get(col, "")))

    def OnRefreshData(self, evt):
        self.table.UpdateData()
        self.table.ResetView()
        self.ForceRefresh()

    def setup(self):
        for n, col in enumerate([c for c in cols if c.active]):
            self.SetColLabelValue(n, col.name.title())

        self.severity = {}

        colours = [wx.RED, wx.RED, wx.RED, wx.RED, wx.WHITE, wx.WHITE, wx.WHITE, wx.WHITE, wx.WHITE]
        for n, c in enumerate(colours):
            attr = wx.grid.GridCellAttr()
            #attr.SetTextColour(wx.BLACK)
            attr.SetBackgroundColour(c)
            #attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.severity[n] = attr

        # test all the events
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        #self.SetRowLabelSize(0)
        #self.SetColLabelSize(0)

    def OnCellLeftClick(self, evt):
        self.log.write("OnCellLeftClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelLeftClick(self, evt):
        self.log.write("OnLabelLeftClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()


class FilterSettings(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        box = wx.BoxSizer(wx.VERTICAL)

        for col in cols:
            panel = wx.Panel(self)
            innerbox = wx.StaticBoxSizer(wx.StaticBox(self, label=col.name), wx.VERTICAL)

            if col.type == "datetime":
                start = wx.calendar.CalendarCtrl(self)
                innerbox.Add(start, 1, wx.ALL)
                end = wx.calendar.CalendarCtrl(self)
                innerbox.Add(end, 1, wx.ALL)
            elif col.type == "hostname":
                filterList = wx.ComboBox(self, choices=["", "localhost", "bob", "fred"])
                innerbox.Add(filterList, 1, wx.ALL)
            else:
                filterList = wx.StaticText(self, -1, "Filter Options Be Here")
                innerbox.Add(filterList, 1, wx.ALL)

            panel.SetSizer(innerbox)
            panel.Layout()

            box.Add(innerbox, 0, wx.ALL)

        self.SetSizer(box)
        self.Layout()


class FilterList(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        box = wx.StaticBoxSizer(wx.StaticBox(self, label="Columns"), wx.VERTICAL)

        for n, col in enumerate(cols):
            cb = wx.CheckBox(self, label=col.name.title())
            cb.SetValue(True)
            cb.Bind(wx.EVT_CHECKBOX, parent.grid.table.OnToggleCol)
            box.Add(cb, 0, wx.ALL)

        refresh = wx.Button(self, label="Refresh")
        refresh.Bind(wx.EVT_BUTTON, parent.OnRefreshData)
        box.Add(refresh, 0, wx.ALL)

        self.SetSizer(box)
        self.Layout()


class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "Ploddle", size=(800, 600))

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        #self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        #self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)

        self.filterSettings = FilterSettings(self)
        self.grid = LogEntryGrid(self, log)
        self.filterList = FilterList(self)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.filterSettings, 0, wx.ALL|wx.EXPAND, 0)
        box.Add(self.grid,           1, wx.ALL|wx.EXPAND, 0)
        box.Add(self.filterList,     0, wx.ALL|wx.EXPAND, 0)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
        self.statusbar = self.CreateStatusBar()

    def OnRefreshData(self, evt):
        self.grid.OnRefreshData(evt)

if __name__ == '__main__':
    import sys
    from wx.lib.mixins.inspection import InspectableApp
    app = InspectableApp(False)
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    #import wx.lib.inspection
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

