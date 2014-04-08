import json
import signal
import time

from mozilla import *


def stopJsonSampler(signum, frame):
    raise KeyboardInterrupt, "Signal handler"

def main():
    ammeterFields = ('current','voltage','time')
    signal.signal(signal.SIGINT, stopJsonSampler)
    powerLog = []
    serialPortName = "/dev/ttyACM0"
    ammeter = MozillaAmmeter(serialPortName, False)

    sampleTimeBeforeEpochOffset = time.time()
    sample = ammeter.getSample(ammeterFields)
    sampleTimeAfterEpochOffset = time.time()
    firstSampleMsCounter = sample['time'].value
    sampleTimeEpochOffset = (sampleTimeAfterEpochOffset + sampleTimeBeforeEpochOffset) * 1000.0 / 2.0 - firstSampleMsCounter;

    try:
    while True:
        sample = ammeter.getSample(ammeterFields)
        if sample is not None:
            current = sample['current'].value / 10.0
            sampleObj = {}
            sampleObj['current'] = current;
            sampleObj['time'] = sample['time'].value;
            powerLog.append(sampleObj)

    except KeyboardInterrupt:
        powerProfile = {}
        powerProfile['sampleTimeEpochOffset'] = sampleTimeEpochOffset
        powerProfile['sampleTimeFirst'] = firstSampleMsCounter
        powerProfile['samples'] = powerLog
        print json.dumps(powerProfile, sort_keys=True,
                    indent=4, separators=(',', ': '))
        ammeter.close()

if __name__ == '__main__':
    main()
