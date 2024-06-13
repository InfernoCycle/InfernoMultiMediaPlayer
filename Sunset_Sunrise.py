import datetime
import time
import math
import re

import numpy
#Website for stuff: https://www.omnicalculator.com/physics/sunrise-sunset#how-to-calculate-the-times-of-sunrise-and-sunset-for-tomorrow

class Sun:
  def __init__(self) -> None:
    self.pi = math.pi
    self.longitude = 83.045753
    self.latitude = 42.331429

  def getFractionalYear(self):
    hour = self.getHour()
    denominator = 365

    if((self.getYear()) % 4 == 0):
      denominator = 366

    if(hour == 0):
      hour = 24

    Y = ((2*self.pi)/(denominator) * (self.getDayOfYear() - 1 + ((hour - 12)/12)))

    return self.convertToRadians(Y)

  def get_eqtime(self):
    eqtime = 229.18 * (0.000075 + (0.001868 * math.cos(self.convertToRadians(self.getFractionalYear())) - (0.032077 * math.sin(self.convertToRadians(self.getFractionalYear()))) - (0.014615 * math.cos(self.convertToRadians((2*self.getFractionalYear())))) - (0.040849 * math.sin(self.convertToRadians((2*self.getFractionalYear()))))))
    return eqtime

  def get_decl(self):
    decl = 0.006918 - (0.399912 * math.cos(self.convertToRadians(self.getFractionalYear()))) + (0.070257 * math.sin(self.convertToRadians(self.getFractionalYear()))) - (0.006758 * math.cos((self.convertToRadians(2 * self.getFractionalYear())))) + (0.000907 * math.sin((self.convertToRadians(2 * self.getFractionalYear()))))
    - (0.002697 * math.cos(self.convertToRadians((3 * self.getFractionalYear())))) + (0.00148 * math.sin ((self.convertToRadians(3 * self.getFractionalYear()))))
    return decl

  def time_offset(self):
    offset = self.get_eqtime() + (4 * self.longitude) - (60 * self.getUTC())
    return offset

  def tst(self):
    tst = (self.getHour()*60) + self.getMinute() + ((self.getSeconds()/60)) + self.time_offset()
    return tst

  def ha(self):
    ha = (self.tst()/4) -180
    return self.convertToDegrees(ha)

  def solarZenith(self):
    co = math.sin(self.latitude) * math.sin(self.get_decl()) + math.cos(self.latitude)*math.cos(self.get_decl())*math.cos(self.ha())
    return co
  
  def solarAzimuth(self):
    co = (math.sin(self.convertToRadians(self.latitude)) - math.sin(self.convertToRadians(self.get_decl()))) / (math.cos(self.convertToRadians(self.latitude)) * math.sin(self.convertToRadians(180)))
    return co

  def sunrise(self):
    
    W = math.acos(-math.tan(self.convertToRadians(45)) * math.tan(self.convertToRadians(-2.82)))
    value = 12 - (W/15)
    return value

  def DeclinationAngle(self):
    X = 3.3727310862250436924932044096558
    A =  X * (math.sin((self.convertToDegrees(360/365)) * (75 + 284)))
    return A

  def convertToDegrees(self, Value):
    degree = Value * (180/math.pi)
    return degree
  
  def convertToRadians(self, Degrees):
    Radians = Degrees * (self.pi/180)
    return Radians

  #series for N's findings
  def __N(self):
    return int(self.__N1() - (self.__N2() * self.__N3()) + self.getDayOfMonth() - 30)

  def __N1(self):
    return int(math.floor(275 * (self.getMonth() / 9)))

  def __N2(self):
    return int(math.floor((self.getMonth() + 9)/12))

  def __N3(self):
    return int(1 + math.floor((self.getYear() - 4 * math.floor(self.getYear() / 4) + 2) / 3))
  
  def display_N(self):
    print("N:" + str(self.N()))
    print("N1: " + str(self.N1()))
    print("N2: " + str(self.N2()))
    print("N3: " + str(self.N3()))
  
  #Series for common date attributes
  def getUTC(self):
    pattern = "[-+][0-9]+:[0-9]+"
    match = re.search(pattern, str(datetime.datetime.now().astimezone()))
    subPattern = "[-+][0-9]+"
    subMatch = re.search(subPattern, str(match.group()))
    return int(subMatch.group())

  def getMinute(self):
    return int(time.strftime("%M", time.localtime(time.time())))

  def getSeconds(self):
    return int(time.strftime("%S", time.localtime(time.time())))

  def getHour(self):
    return int(time.strftime("%H", time.localtime(time.time())))

  def getDayOfYear(self):
    return self.__N()

  def getDayOfMonth(self):
    return int(time.strftime("%d", time.localtime(time.time())))
  
  def getMonth(self):
    return int(time.strftime("%m", time.localtime(time.time())))

  def getYear(self):
    return int(time.strftime("%Y", time.localtime(time.time())))

  def display_Date(self):
    print("Month: " + str(self.getMonth()))
    print("Day: " + str(self.getDayOfMonth()))
    print("Year: " + str(self.getYear()))

if "__main__" == __name__:
  obx = Sun()
  """
  print("Fractional Year: " + str(obx.getFractionalYear()))
  print("EQ_Time: " + str(obx.get_eqtime()))
  print("Angle Declination: " + str(obx.convertToDegrees(obx.get_decl())))
  print("Time_offset: " + str(obx.time_offset()))
  print("True Solar Time: " + str(obx.tst()))
  print("Ha: " + str(obx.ha()))
  print("Solar Zenith Angle: " + str(obx.solarZenith()))
  print("Solar Azimuth Angle: " + str(obx.solarAzimuth()))
  """
