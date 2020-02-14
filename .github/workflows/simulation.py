from tkinter import Tk, Canvas, Menu
from random import random
from math import *
from time import time
from matplotlib import pyplot as pyp
from scipy.interpolate import interp1d
import pygame as pyg

pyg.init()
pyg.display.init()
pyg.joystick.Joystick(0).init()
pj = pyg.joystick.Joystick(0)

mas = Tk()
w,h = (640,640)
x0,y0 = (w/2, h/2)
M,Fx,Fy=0.0,0.0,0.0
oso = 0
osa = 0
aso = 0
asa = 0
timeafter = 50
maxdata = 1000
totalAmper = 0
t1=1
datas = [[0,0,0,0,0,0,0,0,0]] # time , OSO, ASA, OSA, ASO, Fx, Fy, M, totalAmper
starttime = time()
def ktorpm(k):
    return 1500+300*k
def rpmtoamper(x): # G200 verileri kullanıldı
    return 7*(10**-5)*(x**2) - 0.2077*x + 158.49
def timeaft():
    global timeafter
    if timeafter==50:
        timeafter=10**10
    else:
        timeafter=50
        draw()
def save():
    with open("datas{}.txt".format(int(time()-starttime)),"w") as dosya:
        for i in datas:
            dosya.writelines("\n")
            for j in i:
                dosya.write(str(j)+" , ")

def graph(j):
    if len(datas) >= 100:
        axx = [i[0] for i in datas]
        axy = [i[j] for i in datas]
        #axxx = [axx[0]+i/100 for i in range(int(axx[-1]*100))]
        f = interp1d(axx,axy,kind="cubic")
        print({1:"OSO",2:"ASA",3:"OSA",4:"ASO",5:"Fx",6:"Fy",7:"M",8:"totalAmper"}[j] + " Grafiği Eklendi")
        pyp.plot(axx,axy,'.',axx,f(axx))
        pyp.show()

mas.wm_minsize(w,h)
mas.wm_maxsize(w,h)
mas.wm_title("LENTA MARİNE")

men = Menu(mas)
men.add_command(label="Start/Stop", command=timeaft)
men.add_command(label="Save", command=save)
#men.add_command(label="Graph", command=lambda : graph(5))
# time , OSO, ASA, OSA, ASO, Fx, Fy, M
grafik = Menu(mas, tearoff=0)
grafik.add_command(label="ON SOL", command=lambda : graph(1))
grafik.add_command(label="ARKA SAG", command=lambda : graph(2))
grafik.add_command(label="ON SAG", command=lambda : graph(3))
grafik.add_command(label="ARKA SOL", command=lambda : graph(4))
grafik.add_command(label="Fx", command=lambda : graph(5))
grafik.add_command(label="Fy", command=lambda : graph(6))
grafik.add_command(label="M", command=lambda : graph(7))
grafik.add_command(label="totalAmper", command=lambda : graph(8))
men.add_cascade(label="Graph", menu=grafik)


mas.config(menu=men)

can = Canvas(mas, width=w,height=h)
can.pack()

def hesapla():
    global M,Fx,Fy,oso,osa,aso,asa,datas,t1,totalAmper
    pyg.event.pump()
    sl = pj.get_axis(0)//0.01/100# + 0.01#sol # 0.01 düzeltmek için rahatsız etti
    ss = -pj.get_axis(1)//0.01/100#yuk
    saat = pj.get_axis(2)//0.01/100

    #sl = 1-2*random()#pj.get_axis(0)//0.01/100# + 0.01#sol # 0.01 düzeltmek için rahatsız etti
    #ss = 1-2*random()#-pj.get_axis(1)//0.01/100#yuk
    #saat = 1-2*random()#pj.get_axis(2)//0.01/100

    osa = (ss*sqrt(2) + 2*sl/sqrt(2)) / 1.4142135623730951 + saat/sqrt(2)
    asa = (sl-ss)/sqrt(2) / 0.7071067811865475 - saat/sqrt(2)
    oso = -asa - 2*saat/sqrt(2)
    aso = -osa + 2*saat/sqrt(2)

    k = 1 / (max(fabs(oso), fabs(osa), fabs(aso), fabs(asa)) + 1 / 100000)
    k = (k > 1) * 1 + k * (k <= 1)
    # print(k)
    osa = k * osa  # - saat
    asa = k * asa  # + saat
    oso = k * oso  # + saat
    aso = k * aso  # - saat
    totalAmper = (rpmtoamper(ktorpm(osa)) + rpmtoamper(ktorpm(asa)) + rpmtoamper(ktorpm(oso)) + rpmtoamper(ktorpm(aso)))//0.001*0.001
    #print(totalAmper, rpmtoamper(ktorpm(osa)), ktorpm(osa))
    M = oso - osa - aso + asa
    Fx = cos(radians(45)) * (osa + asa - oso - aso) # 2.1323022467358004
    Fy = sin(radians(45)) * (oso + osa - aso - asa) # 2.8216755631054844
    if len(datas) < maxdata:
        datas.append([time()-starttime, oso, asa, osa, aso, Fx, Fy, M, totalAmper])
    else:
        datas = datas[1:maxdata]
        datas.append([time()-starttime, oso, asa, osa, aso, Fx, Fy, M, totalAmper])

def draw():
    global timeafter
    can.delete("all")
    can.create_rectangle(0, 0, w, h, fill="cyan")
    can.create_rectangle(x0-160,y0-160,x0+160,y0+160,width=12)
    can.create_text(w/2,10,text="{}".format(len(datas)), font="Arial 10")
    can.create_text(w/2,30,text="Toplam Çekilen Amper {}A".format(totalAmper), font="Arial 12")
    can.create_text(w/2,45,text="Saat Yönü : {} , İleri/Geri : {} , Sağ/Sol : {}".format(M//0.01/100,Fy//0.01/100,Fx//0.01/100),font="Times 12 bold")
    can.create_line(x0+160-50,y0+160-50,x0+160+50,y0+160+50,width=75) # ASA
    can.create_line(x0-160-50,y0-160-50,x0-160+50,y0-160+50,width=75) # OSO
    can.create_line(x0-160+50,y0+160-50,x0-160-50,y0+160+50,width=75) # ASO
    can.create_line(x0+160+50,y0-160-50,x0+160-50,y0-160+50,width=75) # OSA

    can.create_line(x0+160,y0+160,x0+160+asa*150,y0+160-150*asa,fill="red",width=3) # ASA
    can.create_line(x0-160,y0-160,x0-160-oso*150,y0-160+150*oso,fill="red",width=3) # OSO
    can.create_line(x0-160,y0+160,x0-160-aso*150,y0+160-150*aso,fill="red",width=3) # ASO
    can.create_line(x0+160,y0-160,x0+160+osa*150,y0-160+150*osa,fill="red",width=3) # OSA

    can.create_line(x0,y0,x0+Fx*150,y0)
    can.create_line(x0,y0,x0,y0-Fy*150)
    can.create_oval(x0+M*75,y0+M*75,x0-M*75,y0-M*75)
    #print(osa)
    hesapla()

    mas.after(timeafter,draw)

draw()

mas.bind("<Escape>",lambda x: exit(0))

mas.mainloop()
