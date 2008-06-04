import os
import wx
import traceback


class RotateCanvas(wx.ScrolledWindow):
	def __init__(self, parent, id = -1, size = wx.DefaultSize, bmp = None):
		wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
		self.bmp = bmp
		self.x = self.y = 0
		self.SetBackgroundColour("WHITE")
		self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
		self.SetScrollRate(20, 20)
		self.Bind(wx.EVT_LEFT_UP, self.OnButtonEvent)
		self.Bind(wx.EVT_RIGHT_UP, self.OnButtonEvent)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.outputString("Right click to rotate clockwise, Left click to rotate counter clockwise")

	def getWidth(self):
		return self.maxWidth

	def getHeight(self):
		return self.maxHeight

	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)

	def DoDrawing(self, dc, printing=False):
		dc.BeginDrawing()
		dc.DrawBitmap(self.bmp, 0, 0, True)
		dc.EndDrawing()

	def ConvertEventCoords(self, event):
		newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
		return newpos

	def OnButtonEvent(self, event):
		if event.LeftUp():
			self.bmp = self.bmp.ConvertToImage().Rotate90(False).ConvertToBitmap()
		elif event.RightUp():
			self.bmp = self.bmp.ConvertToImage().Rotate90().ConvertToBitmap()
		self.DoRedraw()

	def DoRedraw(self):
		self.maxWidth  = self.bmp.GetWidth()
		self.maxHeight = self.bmp.GetHeight()
		self.SetVirtualSize((self.maxWidth, self.maxHeight))
		self.buffer = wx.EmptyBitmap(self.maxWidth, self.maxHeight)
		dc = wx.BufferedDC(None, self.buffer)
		dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
		dc.Clear()
		self.DoDrawing(dc)
		self.Refresh()

	def outputString(self, text):
		print text
		self.GetParent().SetStatusText(text)


class RotateFrame(wx.Frame):
	def __init__(self, parent, title, bmp = None, bmpname = ""):
		wx.Frame.__init__(self, parent, -1, title, size=(640, 480), style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
		self.bmpname = bmpname
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.canvas = RotateCanvas(self, size = self.GetClientSize(), bmp = bmp)
		self.canvas.DoRedraw()
		self.CreateStatusBar()
		self.Show(True)

	def OnExit(self, event):
		dlg = wx.MessageDialog(self, 'Save?', 'Close', wx.YES_NO | wx.ICON_QUESTION)
		if dlg.ShowModal() == wx.ID_YES:
			head, tail = os.path.split(self.bmpname)
			fname, ext = os.path.splitext(tail)
			i = 1
			newname = head + "/" + fname + ("_%.4d"%i) + ".jpg"
			while os.path.isfile(newname):
				i = i + 1
				newname = head + "/" + fname + ("_%.4d"%i) + ".jpg"
			print newname
			self.canvas.bmp.SaveFile(newname, wx.BITMAP_TYPE_JPEG)
		dlg.Destroy()
		self.Destroy()


class Canvas(wx.ScrolledWindow):
	def __init__(self, parent, id = -1, size = wx.DefaultSize, bmp = None, bmpname = ""):
		wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
		self.firstCoord = None
		self.x = self.y = 0
		self.SetBackgroundColour("WHITE")
		self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
		self.bmpname = bmpname
		self.bmp = bmp
		self.SetVirtualSize((bmp.GetWidth(), bmp.GetHeight()))
		self.SetScrollRate(20, 20)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftButtonEvent)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.outputString("Click Upper-Left corner")

	def getWidth(self):
		return self.maxWidth

	def getHeight(self):
		return self.maxHeight

	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)

	def DoDrawing(self, dc, printing=False):
		dc.BeginDrawing()
		dc.DrawBitmap(self.bmp, 0, 0, True)
		dc.EndDrawing()

	def ConvertEventCoords(self, event):
		newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
		return newpos

	def OnLeftButtonEvent(self, event):
		if event.LeftUp():
			if self.firstCoord:
				self.secondCoord = self.ConvertEventCoords(event)
				x=self.secondCoord[0]
				if x >= self.bmp.GetWidth():
					x=self.bmp.GetWidth()-1
				y = self.secondCoord[1]
				if y >= self.bmp.GetHeight():
					y=self.bmp.GetHeight()-1
				print "%s"%str((x,y))
				rect = wx.RectPP(self.firstCoord, (x,y))
				bmp = self.bmp.GetSubBitmap(rect)
				frame = RotateFrame(None, u"Rotate Sub-Image", bmp = bmp, bmpname = self.bmpname)
				self.firstCoord = None
				self.secondCoord = None
				self.outputString("Click Upper-Left corner")
			else:
				self.firstCoord = self.ConvertEventCoords(event)
				self.outputString("%s Click Lower-Right corner" % str(self.firstCoord))
		elif event.RightUp():
			self.firstCoord = None
			self.secondCoord = None
			self.outputString("Click Upper-Left corner")

	def DoRedraw(self):
		self.maxWidth  = self.bmp.GetWidth()
		self.maxHeight = self.bmp.GetHeight()
		self.buffer = wx.EmptyBitmap(self.maxWidth, self.maxHeight)
		dc = wx.BufferedDC(None, self.buffer)
		dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
		dc.Clear()
		self.DoDrawing(dc)
		self.Update()

	def outputString(self, text):
		print text
		self.GetParent().SetStatusText(text)


class MainFrame(wx.Frame):
	def evtCloseWindow(self, event):
		self.Close()

	def evtOpen(self, event):
		self.openFile()

	def createMenu(self):
		# Prepare the menu bar
		menuBar = wx.MenuBar()
		# File menu
		menu1 = wx.Menu()
		menu1.Append(101, "&Open")
		menu1.AppendSeparator()
		menu1.Append(104, "&Exit")
		# Add menu to the menu bar
		menuBar.Append(menu1, "&File")
		self.SetMenuBar(menuBar)
		self.Bind(wx.EVT_MENU, self.evtOpen, id=101)
		self.Bind(wx.EVT_MENU, self.evtCloseWindow, id=104)

	def openFile(self):
		wildcard =	"All files (*.*)|*.*|"	\
					"Bitmap (*.bmp)|*.bmp|"	\
					"JPG (*.jpg)|*.jpg|"	\
					"JPEG (*.jpeg)|*.jpeg"
		dlg = wx.FileDialog(self, message="Choose a file", defaultDir=os.getcwd(), defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
		# Show the dialog and retrieve the user response. If it is the OK response, 
		# process the data.
		if dlg.ShowModal() == wx.ID_OK:
			paths = dlg.GetPaths()
			try:
				image = wx.Image(paths[0]).ConvertToBitmap()
				self.canvas = Canvas(self, size = self.GetClientSize(), bmp = image, bmpname = paths[0])
				self.canvas.DoRedraw()
			except:
				print "Invalid file"
		# Destroy the dialog. Don't do this until you are done with it!
		# BAD things can happen otherwise!
		dlg.Destroy()

	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title, size=(640, 480), style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
		self.CreateStatusBar()
		self.createMenu()
		self.SetMinSize((100,100))


class CutNRotGUI(wx.App):
	def OnInit(self):
		wx.SetDefaultPyEncoding("ISO-8859-1")
		self.frame = MainFrame(None, u"Quick Scan")
		self.frame.Show(True)
		self.SetTopWindow(self.frame)
		return True


if __name__ == '__main__':
	try:
		app = CutNRotGUI()
		app.MainLoop()
	except:
		traceback.print_exc()

