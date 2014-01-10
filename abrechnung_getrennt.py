import _mssql
from datetime import *
from sys import *
from Tkinter import *
from ScrolledText import *

def getAccountingString(date, password):
	out = ""

	con = _mssql.connect(server='KASSENPC\JTLWAWI', user='sa', password=password, database='eazybusiness')
	con.execute_query("set dateformat ymd")

	sqlCommand = """
	select kKunde, cKundenNr, cVorname, cName
	from dbo.tkunde
	"""
	con.execute_query(sqlCommand)
	kunden = dict()
	for row in con:
		#print(row)
		kunden[int(row["kKunde"])] = {'id': int(row["kKunde"]), 'name': row["cName"], 'vorname': row["cVorname"]}

	sqlCommand = """
	select dDatum, kKunde, fGesamtSumme
	from dbo.POS_Bon
	where dDatum >= cast('%s 00:00:00' as smalldatetime)
		and dDatum < cast('%s 23:59:59' as smalldatetime)
		and kBonStorno = 0
	order by kKunde, dDatum
	""" % (date, date)

	con.execute_query(sqlCommand)
	for row in con:
		out = out + '%s  %12s    %7.2f EUR\n' % (row["dDatum"], kunden[row["kKunde"]]["name"], row["fGesamtSumme"])

	################################
	# Gesamtsumme
	################################
	sqlCommand = """
	select fGesamtSumme, fSumme1, fSumme2, fSumme3, fMwSt1, fMwSt2, fMwSt3, kKunde
	from dbo.POS_Bon
	where dDatum >= cast('%s 00:00:00' as smalldatetime)
		and dDatum < cast('%s 23:59:59' as smalldatetime)
		and kBonStorno = 0
	""" % (date, date)

	#print(sqlCommand)
	mwStList = set()	# set of all used MwSt percent values
	sumByKundeByMwSt = dict()
	con.execute_query(sqlCommand)
	for row in con:
		kId = int(row["kKunde"])
		mwStList.add(int(row["fMwSt1"]))
		mwStList.add(int(row["fMwSt2"]))
		mwStList.add(int(row["fMwSt3"]))

		if sumByKundeByMwSt.get(kId) is None:
			sumByKundeByMwSt[kId] = dict()

		if sumByKundeByMwSt[kId].get(int(row["fMwSt1"])) is None:
			sumByKundeByMwSt[kId][int(row["fMwSt1"])] = 0.0
		sumByKundeByMwSt[kId][int(row["fMwSt1"])] += round(row["fSumme1"], 2)

		if sumByKundeByMwSt[kId].get(int(row["fMwSt2"])) is None:
			sumByKundeByMwSt[kId][int(row["fMwSt2"])] = 0.0
		sumByKundeByMwSt[kId][int(row["fMwSt2"])] += round(row["fSumme2"], 2)

		if sumByKundeByMwSt[kId].get(int(row["fMwSt3"])) is None:
			sumByKundeByMwSt[kId][int(row["fMwSt3"])] = 0.0
		sumByKundeByMwSt[kId][int(row["fMwSt3"])] += round(row["fSumme3"], 2)

	out = out + str(sumByKundeByMwSt)

	con.close()
	return out


def writeToFile(filename, text):
	pass

class UI:
	def __init__(self, password):
		self.password = password

		self.window = Tk()

		self.day = StringVar()
		self.day.set(date.today().day)
		self.month = StringVar()
		self.month.set(date.today().month)
		self.year = StringVar()
		self.year.set(date.today().year)
		self.text = StringVar()

		self.dateFrame = Frame(self.window)
		self.dateFrame["padx"] = 20
		self.dateFrame["pady"] = 10
		self.dateFrame.pack()

		self.dayL = Label(self.dateFrame)
		self.dayL["text"] = "Tag:"
		self.dayL.pack(side='left', padx=10)
		self.dayI = Entry(self.dateFrame)
		self.dayI["width"] = 5
		self.dayI["textvariable"] = self.day
		self.dayI.pack(side='left', padx=5)

		self.monthL = Label(self.dateFrame)
		self.monthL["text"] = "Monat:"
		self.monthL.pack(side='left', padx=5)
		self.monthI = Entry(self.dateFrame)
		self.monthI["width"] = 5
		self.monthI["textvariable"] = self.month
		self.monthI.pack(side='left', padx=5)

		self.yearL = Label(self.dateFrame)
		self.yearL["text"] = "Jahr:"
		self.yearL.pack(side='left', padx=5)
		self.yearI = Entry(self.dateFrame)
		self.yearI["width"] = 5
		self.yearI["textvariable"] = self.year
		self.yearI.pack(side='left', padx=5)

		self.button = Button(self.dateFrame)
		self.button["text"] = "Erstellen"
		self.button["width"] = 20
		self.button["command"] = self.buttonCallback
		self.button.pack(side='left', padx=20)

		self.textI = ScrolledText(self.window)
		self.updateTextI("e")
		self.textI.pack()

		self.exportB = Button(self.window)
		self.exportB["text"] = "Export"
		self.exportB["width"] = 20
		self.exportB["command"] = self.exportButtonCallback
		self.exportB.pack(pady=15)

		self.buttonCallback()

		self.window.mainloop()

	def updateTextI(self, t):
		self.textI.delete("1.0", END)
		self.textI.insert(END, t)

	def buttonCallback(self):
		d = "%s-%s-%s" % (self.year.get(), self.month.get(), self.day.get())
		#print(getAccountingString(d))
		self.updateTextI(getAccountingString(d, self.password))

	def exportButtonCallback(self):
		pass

if __name__== '__main__':
	if len(argv) < 2:
		print('usage: python abrechnung.py <<DB password>>')
		exit(1)
	ui = UI(argv[1])
