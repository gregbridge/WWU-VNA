"""
Python script to get the accuracy of the TIME command.

Author: Jacob Priddy
Date: 4/23/18

WORK IN PROGRESS
"""

import time, serial, numpy, statistics, cmath


def average(arr):
    return sum(arr) / len(arr)


print("Enter the com port")
port = str(input())

print("Enter the frequency in MHz")
fMin = int(float(input()) * 1e6)

print("Enter number of samples")
samp = int(input())

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
command = "^SAMPLERATE,"+"$\n"
ser.write(command.encode())

Fs = int(ser.readline())
N = int(ser.readline().decode().strip(' \n'))
F_IF = int(ser.readline().decode().strip(' \n'))

T = 1./float(Fs)


endRef = []
endMeas = []

for x in range(samp):
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

ref = []
meas = []
H1 = []
H3 = []
H5 = []
H7 = []

for x in range(samp):
    reffft = numpy.fft.fft(endRef[x])
    measfft = numpy.fft.fft(endMeas[x])
    ref.append(reffft[int(F_IF*N/Fs+1)])
    meas.append(measfft[int(F_IF*N/Fs+1)])
    H1.append(measfft[int(F_IF * N / Fs + 1)] / reffft[int(F_IF * N / Fs + 1)])
    H3.append(measfft[int(3 * F_IF * N / Fs + 1)] / reffft[int(3 * F_IF * N / Fs + 1)])
    H5.append(measfft[int(5 * F_IF * N / Fs + 1)] / reffft[int(5 * F_IF * N / Fs + 1)])
    H7.append(measfft[int(7 * F_IF * N / Fs + 1)] / reffft[int(7 * F_IF * N / Fs + 1)])

    print('Ref: ' + str(ref[x]) + '\n')
    print('Meas: ' + str(meas[x]) + '\n')
    print('H1: ' + str(H1[x]) + '\n')
    print('H3: ' + str(H3[x]) + '\n')
    print('H5: ' + str(H5[x]) + '\n')
    print('H7: ' + str(H7[x]) + '\n')

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

print('H1 Magnitude Mean: ' + str(magH1bar) + '\n')
print('H3 Magnitude Mean: ' + str(magH3bar) + '\n')
print('H5 Magnitude Mean: ' + str(magH5bar) + '\n')
print('H7 Magnitude Mean: ' + str(magH7bar) + '\n')

print('H1 Phase Mean: ' + str(phaseH1bar) + '\n')
print('H3 Phase Mean: ' + str(phaseH3bar) + '\n')
print('H5 Phase Mean: ' + str(phaseH5bar) + '\n')
print('H7 Phase Mean: ' + str(phaseH7bar) + '\n')

print('H1 Magnitude Standard Deviation: ' + str(statistics.stdev(magH1, magH1bar)) + '\n')
print('H3 Magnitude Standard Deviation: ' + str(statistics.stdev(magH3, magH3bar)) + '\n')
print('H5 Magnitude Standard Deviation: ' + str(statistics.stdev(magH5, magH5bar)) + '\n')
print('H7 Magnitude Standard Deviation: ' + str(statistics.stdev(magH7, magH7bar)) + '\n')

print('H1 Phase Standard Deviation: ' + str(statistics.stdev(phaseH1, phaseH1bar)) + '\n')
print('H3 Phase Standard Deviation: ' + str(statistics.stdev(phaseH3, phaseH3bar)) + '\n')
print('H5 Phase Standard Deviation: ' + str(statistics.stdev(phaseH5, phaseH5bar)) + '\n')
print('H7 Phase Standard Deviation: ' + str(statistics.stdev(phaseH7, phaseH7bar)) + '\n')

print('H1 Magnitude Variance: ' + str(statistics.variance(magH1, magH1bar)) + '\n')
print('H3 Magnitude Variance: ' + str(statistics.variance(magH3, magH3bar)) + '\n')
print('H5 Magnitude Variance: ' + str(statistics.variance(magH5, magH5bar)) + '\n')
print('H7 Magnitude Variance: ' + str(statistics.variance(magH7, magH7bar)) + '\n')

print('H1 Phase Variance: ' + str(statistics.variance(phaseH1, phaseH1bar)) + '\n')
print('H3 Phase Variance: ' + str(statistics.variance(phaseH3, phaseH3bar)) + '\n')
print('H5 Phase Variance: ' + str(statistics.variance(phaseH5, phaseH5bar)) + '\n')
print('H7 Phase Variance: ' + str(statistics.variance(phaseH7, phaseH7bar)) + '\n')