import wx
from wx.adv import Animation, AnimationCtrl
#from crawler import PartSurfer

class MyDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("Crawler - PartSurfer")
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTINACTIVECAPTION))

        self.pathDirect = ''
        self.filename = ''

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.StdDialogButtonSizer()
        self.SetSizer(sizer_1)

        self.btn_LOAD = wx.Button(self, wx.ID_ANY, "Load File")
        self.btn_SAVE = wx.Button(self, wx.ID_SAVE, "")
        self.btn_SAVE.SetDefault()
        self.btn_SAVE.Disable()
        self.btn_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        
        #self.img = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("Crawler-Partsurfer\load.gif", wx.BITMAP_TYPE_ANY))
        #self.img.SetSize(self.img.GetBestSize())
        #self.img = wx.Image('./load.png', type=wx.BITMAP_TYPE_ANY)

        self.gif = Animation('./load.gif')
        self.ctrl = AnimationCtrl(self, -1, self.gif)

        sizer_1.Add(sizer_2, 3, wx.EXPAND, 0)
        sizer_1.Add(sizer_3, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 4)
        sizer_2.Add(self.btn_LOAD, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        #sizer_2.Add(self.img, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(self.ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        sizer_3.AddButton(self.btn_SAVE)
        sizer_3.AddButton(self.btn_CANCEL)
        sizer_3.Realize()
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.btn_SAVE.GetId())
        self.SetEscapeId(self.btn_CANCEL.GetId())
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.loadFile, self.btn_LOAD)
        self.Bind(wx.EVT_BUTTON, self.saveFile, self.btn_SAVE)

    def loadFile(self, e):
        with wx.FileDialog(self, 'Open File Text', wildcard="Text files (*.txt)|*.txt",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.filename = fileDialog.GetFilename()
            self.path = fileDialog.GetDirectory() + '\\'
            try:
                with open(self.path+self.filename, 'r') as file:
                    self.file = file.read()
                self.btn_SAVE.Enable()
                self.ctrl.Play()
            except IOError:
                wx.LogError('Cannot Open File {}')
    
    def saveFile(self, e):
        print (self.file)
        self.btn_SAVE.Disable()

    
class MyApp(wx.App):
    def OnInit(self):
        self.dialog = MyDialog(None, wx.ID_ANY, "")
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return True

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
