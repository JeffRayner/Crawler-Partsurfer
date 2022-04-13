import wx
from wx.adv import Animation, AnimationCtrl
import wx.lib.newevent as NE
from threading import Thread
from crawler import PartSurfer

result_evt, EVT_RESULT = NE.NewEvent()

class Window(wx.Dialog):
    __path:str = ''
    __fileName:str = None
    __file:str = None
    __crawler:PartSurfer = None

    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("Crawler - PartSurfer")
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTINACTIVECAPTION))
        
        #Initialization Layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.StdDialogButtonSizer()
        self.SetSizer(sizer_1)

        self.btn_LOAD = wx.Button(self, wx.ID_ANY, "Load File")
        self.btn_SAVE = wx.Button(self, wx.ID_SAVE, "")
        self.btn_SAVE.SetDefault()
        self.btn_SAVE.Disable()
        self.btn_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        
        self.gif1 = Animation('load.gif')
        self.gif2 = Animation('done.gif')
        self.ctrl = AnimationCtrl(self, -1, self.gif1)

        sizer_1.Add(self.sizer_2, 3, wx.EXPAND, 0)
        sizer_1.Add(sizer_3, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 4)
        self.sizer_2.Add(self.btn_LOAD, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.sizer_2.Add(self.ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        sizer_3.AddButton(self.btn_SAVE)
        sizer_3.AddButton(self.btn_CANCEL)
        sizer_3.Realize()
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.btn_SAVE.GetId())
        self.SetEscapeId(self.btn_CANCEL.GetId())
        self.Layout()
        self.ctrl.Hide()
        
        #Set Action 
        self.Bind(wx.EVT_BUTTON, self.loadFile, self.btn_LOAD)
        self.Bind(wx.EVT_BUTTON, self.saveFile, self.btn_SAVE)
        self.Bind(EVT_RESULT, self.replaceIMG)
        
    def loadFile(self, e):
        with wx.FileDialog(self, 'Open File Text', wildcard="Text files (*.txt)|*.txt",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            self.__fileName = dialog.GetFilename()
            self.__path = dialog.GetDirectory() + '\\'
        try:
            with open(self.__path + self.__fileName, 'r') as file:
                self.__file = file.read()
        except IOError:
            wx.LogError('Cannot open file: {}'.format(self.__fileName))
            return
        
        self.thd = Thread(target=self.find, args=(), daemon=True)
        self.thd.start()
        wx.PostEvent(self, result_evt(gif=1, hide=False) )
    
    def find(self):
        self.btn_LOAD.Disable()
        self.__crawler = PartSurfer(self.__file)
        self.__crawler.find()
        self.btn_SAVE.Enable()
        wx.PostEvent(self, result_evt(gif=2, hide=False) )
        
    def replaceIMG(self, evt):
        gif = {1:self.gif1, 2:self.gif2}[evt.gif]
        self.ctrl.Destroy()
        self.ctrl = AnimationCtrl(self, -1, gif)
        self.sizer_2.Add(self.ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.ctrl.Play()
        self.ctrl.Show()
        self.Layout()
        if evt.hide:
            self.ctrl.Hide()

    def saveFile(self, e):
        with wx.FileDialog(self, 'Save File CSV', wildcard="CSV files (*.csv)|*.csv",
                       style=wx.FD_SAVE, defaultDir=self.__path) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            self.__crawler.export2Csv(dialog.GetPath())
            wx.LogMessage('File has saved')
        
        self.ctrl.Stop()
        self.btn_LOAD.Enable()
        self.btn_SAVE.Disable()

class MyApp(wx.App):
    def OnInit(self):
        self.dialog = Window(None, wx.ID_ANY, "")
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return True

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
