"""
Python script to test the accuracy of the TIME command.
Author: Jacob Priddy
Date: 4/27/18
"""
# This is pyserial
import serial
import numpy
import statistics
import cmath
import datetime
import os
import time
import matplotlib.pyplot as plt


def average(arr):
    return sum(arr) / len(arr)


print("Enter the com port")
port = str(input())

print("Enter the frequency in MHz")
fMin = int(float(input()) * 1e6)

print("Enter number of samples")
samp = int(input())

start = time.time()

filename = str(os.path.splitext(os.path.basename(__file__))[0]) + "_" + str(datetime.datetime.now()).replace(":", "-")\
    .replace(".", "-").replace(" ", "_") + ".dat"

if not os.path.exists("measurements"):
    os.makedirs("measurements")

file = open("measurements/" + filename, 'w+')

try:
    ser = serial.Serial(port, 115200, timeout=3)
except serial.serialutil.SerialException:
    print("Could not open the port")
    exit()

if not ser.is_open:
    print("Could not open port")
    exit()

time.sleep(1)
ser.flush()
command = "^SAMPLERATE,1"+"$\n"
ser.write(command.encode())

Fs = int(ser.readline())
N = int(ser.readline().decode().strip(' \n'))
F_IF = int(ser.readline().decode().strip(' \n'))

T = 1./float(Fs)

file.write("Time Test\n")
file.write("Frequency = " + str(fMin) + '\n')
file.write("Samples = " + str(samp) + '\n')
file.write("Port = " + str(port) + '\n')

file.write("FS = " + str(Fs) + '\n')
file.write("N = " + str(N) + '\n')
file.write("F_IF = " + str(F_IF) + '\n')
file.write("T = " + str(T) + '\n\n\n')

endRef = []
endMeas = []

for x in range(samp):
    print("Getting " + str(x) + '\n')
    command = "^TIME," + str(fMin) + "$\n"
    ser.write(command.encode())
    ref = ser.readline().decode()
    meas = ser.readline().decode()

    ref = ref.split(',')
    meas = meas.split(',')
    refSanitized = [int(x.strip(' \n')) for x in ref if x.strip(' \n')]
    measSanitized = [int(x.strip(' \n')) for x in meas if x.strip(' \n')]

    ref = [x - average(refSanitized) for x in refSanitized]
    meas = [x - average(measSanitized) for x in measSanitized]

    endRef.append(ref)
    endMeas.append(meas)

ser.close()


plt.plot(numpy.arange(0, len(endRef[0]) / Fs, 1/Fs), endRef[0],numpy.arange(0, len(endMeas[0]) / Fs, 1/Fs), endMeas[0])
plt.show()

#plt.plot(numpy.arange(0, len(endMeas[0]) / Fs, 1/Fs), endMeas[0])
#plt.show()


ref = []
meas = []
H1 = []
H3 = []
H5 = []
H7 = []

window = numpy.hanning(N)

for x in range(samp):
    print("Computing " + str(x) + '\n')
    for y in range(len(endRef[x])):
        endRef[x][y] *= window[y]

    for y in range(len(endMeas[x])):
        endMeas[x][y] *= window[y]

    reffft = numpy.fft.fft(endRef[x])
    measfft = numpy.fft.fft(endMeas[x])
    ref.append(reffft[int(F_IF*N/Fs+1)])
    meas.append(measfft[int(F_IF*N/Fs+1)])
    H1.append(measfft[int(F_IF * N / Fs + 1)] / reffft[int(F_IF * N / Fs + 1)])
    H3.append(measfft[int(3 * F_IF * N / Fs + 1)] / reffft[int(3 * F_IF * N / Fs + 1)])
    H5.append(measfft[int(5 * F_IF * N / Fs + 1)] / reffft[int(5 * F_IF * N / Fs + 1)])
    H7.append(measfft[int(7 * F_IF * N / Fs + 1)] / reffft[int(7 * F_IF * N / Fs + 1)])

    file.write("Measurement " + str(x + 1) + '\n')
    file.write('Ref: ' + str(ref[x]) + '\n')
    file.write('Meas: ' + str(meas[x]) + '\n')
    file.write('H1: ' + str(H1[x]) + '\n')
    file.write('H3: ' + str(H3[x]) + '\n')
    file.write('H5: ' + str(H5[x]) + '\n')
    file.write('H7: ' + str(H7[x]) + '\n\n\n')

X0 = numpy.fft.fftshift(numpy.fft.fft(endRef[0])/N)
f = numpy.arange(-1/(2*T),1/(2*T),1/(N*T))
plt.plot(f,numpy.abs(X0))
plt.show()

X1 = numpy.fft.fftshift(numpy.fft.fft(endRef[0])/N)
plt.plot(f,numpy.abs(X1))
plt.show()

magH1 = [numpy.absolute(x) for x in H1]
magH3 = [numpy.absolute(x) for x in H3]
magH5 = [numpy.absolute(x) for x in H5]
magH7 = [numpy.absolute(x) for x in H7]

phaseH1 = [cmath.phase(x)*180/cmath.pi for x in H1]
phaseH3 = [cmath.phase(x)*180/cmath.pi for x in H3]
phaseH5 = [cmath.phase(x)*180/cmath.pi for x in H5]
phaseH7 = [cmath.phase(x)*180/cmath.pi for x in H7]


# Store mean calculations for computing variances later
magH1bar = statistics.mean(magH1)
magH3bar = statistics.mean(magH3)
magH5bar = statistics.mean(magH5)
magH7bar = statistics.mean(magH7)

phaseH1bar = statistics.mean(phaseH1)
phaseH3bar = statistics.mean(phaseH3)
phaseH5bar = statistics.mean(phaseH5)
phaseH7bar = statistics.mean(phaseH7)

refmean = average([numpy.abs(x) for x in ref])
measmean = average([numpy.abs(x) for x in meas])

refstdv = statistics.stdev([numpy.abs(x) for x in ref])
measstdv = statistics.stdev([numpy.abs(x) for x in meas])

file.write('Reference Magnitude Mean: ' + str(refmean) + '\n')
file.write('Measured Magnitude Mean: ' + str(measmean) + '\n\n')

file.write('Reference Magnitude Standard Deviation: ' + str(refstdv) + '\n')
file.write('Measured Magnitude Standard Deviation: ' + str(measstdv) + '\n\n')

file.write('Standard deviation percent off mean ref: ' + str(refstdv/refmean * 100) + '%\n')
file.write('Standard deviation percent off mean meas: ' + str(measstdv/measmean * 100) + '%\n\n')

file.write('Reference Real Part Standard Deviation: ' + str(statistics.stdev([numpy.real(x) for x in ref])) + '\n')
file.write('Reference Imaginary Part Standard Deviation: ' + str(statistics.stdev([numpy.imag(x) for x in ref])) + '\n\n')

file.write('Measured Real Part Standard Deviation: ' + str(statistics.stdev([numpy.real(x) for x in meas])) + '\n')
file.write('Measured Imaginary Part Standard Deviation: ' + str(statistics.stdev([numpy.imag(x) for x in meas])) + '\n\n')

file.write('H1 Magnitude Mean: ' + str(magH1bar) + '\n')
file.write('H3 Magnitude Mean: ' + str(magH3bar) + '\n')
file.write('H5 Magnitude Mean: ' + str(magH5bar) + '\n')
file.write('H7 Magnitude Mean: ' + str(magH7bar) + '\n\n')

file.write('H1 Phase Mean: ' + str(phaseH1bar) + '\n')
file.write('H3 Phase Mean: ' + str(phaseH3bar) + '\n')
file.write('H5 Phase Mean: ' + str(phaseH5bar) + '\n')
file.write('H7 Phase Mean: ' + str(phaseH7bar) + '\n\n')

file.write('H1 Magnitude Standard Deviation: ' + str(statistics.stdev(magH1, magH1bar)) + '\n')
file.write('H3 Magnitude Standard Deviation: ' + str(statistics.stdev(magH3, magH3bar)) + '\n')
file.write('H5 Magnitude Standard Deviation: ' + str(statistics.stdev(magH5, magH5bar)) + '\n')
file.write('H7 Magnitude Standard Deviation: ' + str(statistics.stdev(magH7, magH7bar)) + '\n\n')

file.write('H1 Phase Standard Deviation: ' + str(statistics.stdev(phaseH1, phaseH1bar)) + '\n')
file.write('H3 Phase Standard Deviation: ' + str(statistics.stdev(phaseH3, phaseH3bar)) + '\n')
file.write('H5 Phase Standard Deviation: ' + str(statistics.stdev(phaseH5, phaseH5bar)) + '\n')
file.write('H7 Phase Standard Deviation: ' + str(statistics.stdev(phaseH7, phaseH7bar)) + '\n\n')

file.write('H1 Magnitude Variance: ' + str(statistics.variance(magH1, magH1bar)) + '\n')
file.write('H3 Magnitude Variance: ' + str(statistics.variance(magH3, magH3bar)) + '\n')
file.write('H5 Magnitude Variance: ' + str(statistics.variance(magH5, magH5bar)) + '\n')
file.write('H7 Magnitude Variance: ' + str(statistics.variance(magH7, magH7bar)) + '\n\n')

file.write('H1 Phase Variance: ' + str(statistics.variance(phaseH1, phaseH1bar)) + '\n')
file.write('H3 Phase Variance: ' + str(statistics.variance(phaseH3, phaseH3bar)) + '\n')
file.write('H5 Phase Variance: ' + str(statistics.variance(phaseH5, phaseH5bar)) + '\n')
file.write('H7 Phase Variance: ' + str(statistics.variance(phaseH7, phaseH7bar)) + '\n')

file.close()

print("DONE! CHECK measurements/" + filename + '\n')
print("Total TIme: " + str(time.time() - start) + " seconds\n")