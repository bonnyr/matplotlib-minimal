import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from datetime import datetime
from dateutil import parser
import csv
import argparse
import re
import glob


stateFields = ['counter', 'device', 'date', 'sample']

mapV6 = {
    'sysIpStatResetStats': 'sysIp6StatResetStats',
    'sysIpStatTx': 'sysIp6StatTx',
    'sysIpStatRx': 'sysIp6StatRx',
    'sysIpStatDropped': 'sysIp6StatDropped',
    'sysIpStatRxFrag': 'sysIp6StatRxFrag',
    'sysIpStatRxFragDropped': 'sysIp6StatRxFragDropped',
    'sysIpStatTxFrag': 'sysIp6StatTxFrag',
    'sysIpStatTxFragDropped': 'sysIp6StatTxFragDropped',
    'sysIpStatReassembled': 'sysIp6StatReassembled',
    'sysIpStatErrCksum': 'sysIp6StatErrCksum',
    'sysIpStatErrLen': 'sysIp6StatErrLen',
    'sysIpStatErrMem': 'sysIp6StatErrMem',
    'sysIpStatErrRtx': 'sysIp6StatErrRtx',
    'sysIpStatErrProto': 'sysIp6StatErrProto',
    'sysIpStatErrOpt': 'sysIp6StatErrOpt',
    'sysIpStatErrReassembledTooLong': 'sysIp6StatErrReassembledTooLong',
    'sysIpStatNbrPbqFullDropped': 'sysIp6StatNbrPbqFullDropped',
    'sysIpStatNbrUnreachableDropped': 'sysIp6StatNbrUnreachableDropped',
    'sysIpStatMcastTx': 'sysIp6StatMcastTx',
    'sysIpStatMcastRx': 'sysIp6StatMcastRx',
    'sysIpStatErrMcastRpf': 'sysIp6StatErrMcastRpf',
    'sysIpStatErrMcastWrongIf': 'sysIp6StatErrMcastWrongIf',
    'sysIpStatErrMcastNoRoute': 'sysIp6StatErrMcastNoRoute',
    'sysIpStatErrMcastRouteLookupTimeout': 'sysIp6StatErrMcastRouteLookupTimeout',
    'sysIpStatErrMcastMaxPendingPackets': 'sysIp6StatErrMcastMaxPendingPackets',
    'sysIpStatErrMcastMaxPendingRoutes': 'sysIp6StatErrMcastMaxPendingRoutes',
}

EXPECTED_STAT_CNT = 52


def errExit(err):
    print(err)
    sys.exit(-1)


def parseArgs():
    parser = argparse.ArgumentParser(
        description='Maintain counter snapshot and plot them')
    parser.add_argument('stateFile', metavar='state', type=str,
                        nargs=1, help='path to state file. Required')
    parser.add_argument('input', metavar='input', type=str, nargs=1,
                        help='path to input directory containing SNMP counter data. Required')
    parser.add_argument('output', metavar='output', type=str, nargs=1,
                        help='path to output directory where generated graphs are stored. Required')
    parser.add_argument('-m', '--metric', dest='metrics', action='append',
                        help='name of counter to plot. Optional. If no counters are specified, all counters are plotted')
    parser.add_argument('-t', '--trim', dest='trim', type=int, nargs=1)

    return parser.parse_args()


def setCounter(counterMaps, c, h, d, s):
    if c not in counterMaps:
        counterMaps[c] = {}
    cm = counterMaps[c]
    if not h in cm:
        cm[h] = {}
    hm = cm[h]
    hm[d] = s


def buildState(stateFile):
    counterMaps = {}
    if os.path.isfile(stateFile):
        with open(stateFile, 'r') as sf:
            r = csv.DictReader(sf, fieldnames=stateFields)
            for row in r:
                d = row['date']
                h = row['device']
                c = row['counter']
                s = int(row['sample'])

                setCounter(counterMaps, c, h, d, s)
                # counterMaps[c][d] = s

    return counterMaps


def trimState(counterMaps, count):
    for c in counterMaps:
        cm = counterMaps[c]
        for h in cm:
            hm = cm[h]
            shm = dict(sorted(hm.items()))
            cnt = len(shm.keys()) - count

            while cnt > 0:
                k = next(iter(shm))
                shm.pop(k)
                cnt = cnt - 1
            cm[h] = shm


def processSnapshot(counterMaps, snapshotFile):
    m = re.match(
        '(.*/)?(?P<device>[^-]+)-((?P<date>[^-]+)(-(?P<time>[^.]+))?)\..*$', snapshotFile)
    if not m:
        errExit('snapshotFile must be formatted using <device>-<date>')

    device = m.group('device')
    date = m.group('date')

    print('processing sample snapshot for %s in %s' % (device, snapshotFile))
    # device = ''
    # date = ''
    statCnt = 0
    with open(snapshotFile) as f:
        # First line contents is the date
        # Time stamp MUST be formatted as: Sun Feb 19 13:43:46 JST 2023
        # dateline = f.readline().strip()
        # date = datetime.strftime(datetime.strptime(dateline, "%a %b %d %H:%M:%S %Z %Y"), "%Y%m%d-$H%M")
        # date = datetime.strftime(parser.parse(dateline), "%Y%m%d-%H%M")
        for l in f.readlines():
            l = l.strip()
            # if not device:
            #     h = re.match('hostname: (?P<device>.*)', l)
            #     if h:
            #         device = h.group('device')
            #         continue

            m = re.match(
                '^.*::(?P<counter>[^.]+)\.0 = .*: (?P<sample>[0-9]+)$', l)
            if not m:
                continue

            # if not device:
            #     errExit('stat line encountered but hostname is not present in file %s' %snapshotFile)

            statCnt += 1
            setCounter(counterMaps, m.group('counter'),
                       device, date, int(m.group('sample')))

        if statCnt < EXPECTED_STAT_CNT:
            errExit('too few counters when processing file %s' % snapshotFile)


def plotCounter(counterMaps, counter, outdir):
    cm = counterMaps[counter]
    v6Counter = mapV6[counter]
    cm6 = counterMaps[v6Counter]

    fig, axis = plt.subplots(2)
    fig.set_size_inches(20, 10)
    fig.tight_layout(pad=8)
    plt.subplots_adjust(right=0.7, left=0.05)

    colmap = plt.get_cmap('gist_rainbow')

    colors = [(0.0, 1.0, 0.0), (0.8875614242477516, 0.002607003660221041, 0.9083451411317437), (0.025342466927977036, 0.583790402431076, 0.9424962233547738), 
              (1.0, 0.5, 0.0), (0.142638317477765, 0.0008628083508124273, 0.8437957984629576), (0.7143253785953796, 0.9998191925860676, 0.241646972520691), 
              (0.2770836616206197, 0.4925008699550002, 0.2746419692909311), (0.68387772016019, 0.0053460116555795745, 0.20889073025884752), 
              (0.7374307831886544, 0.5226102343804195, 0.9171271865363856), (0.14147197224193075, 0.9997309626267589, 0.6235482537904758), 
              (0.5, 1.0, 1.0), (0.9859226956982294, 0.7154508637839484, 0.5285606629093574), (0.9408748076714101, 0.32981432613427375, 0.47997882437779826), 
              (0.49281942275655166, 0.22133937194437991, 0.6259654808990275), (0.0702017282813191, 0.12693105882748024, 0.4031583427602502), 
              (0.5151887764486309, 0.7401878501476061, 0.5852370426153457), 
              (0.4308894673309406, 0.7855076876560456, 0.02379856228069066), (0.0, 1.0, 1.0), (0.32243029735902307, 0.22558607711606515, 0.02954173492462775), 
              (0.008987026385870678, 0.5891021969926521, 0.5634057013882958), (0.6124930399997662, 0.4957909373227395, 0.04901743400205372), 
              (0.01737671245628869, 0.6771311073511073, 0.06585282497119915), (1.0, 0.0, 0.5), (0.34723639206187806, 0.3649039261350048, 0.9947904261421493), 
              (0.9884624047660817, 0.8275303601284423, 0.08328144043749364), (1.0, 0.0, 0.0), (0.5, 0.0, 1.0),
              (0.02819482533877704, 0.2676633407749296, 0.7308174252989241), (0.05191872616857829, 0.8768966551518127, 0.31657470281307576), 
              (0.6607103543961413, 0.49282728598354497, 0.4741740216670376), (1.0, 1.0, 0.5), (0.3474032008693744, 0.7322709197360844, 0.987274304693787), 
              (0.9520254004796572, 0.2874802544309678, 0.8927888996384485), (0.32348151799695246, 0.5413841994068044, 0.7360615643153897), 
              (0.721795292758247, 0.9513206460949599, 0.7218165398903669), (0.6220591934725498, 0.2532871408867189, 0.31286313580766445), 
              (0.02380468709907091, 0.4055819445439466, 0.0003723323408778567), (0.7019796224646833, 0.012031941769182208, 0.612325984400378), 
              (0.40538770061285956, 0.9636852431070013, 0.4149592334347375), (0.8306972568120738, 0.2765481670754282, 0.03284841786867754), 
              (0.3561570081442724, 0.005150491668617807, 0.22206028181290616), (0.9938962636433958, 0.7111857866916025, 0.9093630273462278), 
              (0.6459153589037597, 0.7301536260416168, 0.2812820649607697), (0.7103985470710953, 0.7688501542672411, 0.9958964262782527), 
              (0.15986799615979974, 0.7691339455731285, 0.695755717335326), (0.3854920203369754, 0.012275830108376962, 0.5354509233493709), 
              (0.681111811821304, 0.1879410388854883, 0.8745689772414837), (0.3181843982781699, 0.2642489034882841, 0.39800892769118257), 
              (0.024620007792702236, 0.3753889978341748, 0.38569396940892864), (0.8875372670144295, 0.5458267711276514, 0.2869520218324685)]

    def plotFigure(name, m, row):
        axis[row].set_title('%s - generated at %s' %
                            (name, datetime.now().strftime('%Y%m%d-%H%M')))
        colNdx = 0
        for h in m:
            ds = m[h]
            sds = dict(sorted(ds.items()))

            v = list(sds.values())
            dvl = [0] + [v[i+1] - v[i] for i in range(len(v)-1)]
            kl = list(sds.keys())
            # print( 'plotting %s: %s' %(name, dvl))
            axis[row].tick_params(axis='x', rotation=45)
            axis[row].plot(kl, dvl, 'o-', label=h, color=colors[colNdx % 50])
            axis[row].text(kl[-1], dvl[-1], h[len(h)-2:], bbox=dict(boxstyle="square,pad=0.3", fc="lightblue"))
            colNdx += 1

        if row == 0:
            # , ncol=int(len(m)/30)+1)
            axis[row].legend(bbox_to_anchor=(1.04, 1), loc="upper left")

    plotFigure(counter, cm, 0)
    plotFigure(v6Counter, cm6, 1)

    fn = os.path.join(outdir, counter + '-' +
                      datetime.now().strftime('%Y%m%d') + '.png')
    print('saving: ' + fn)
    plt.savefig(fn, dpi=100)
    plt.show()
    plt.close()


def plotCounters(counterMaps, device):
    for counter in counterMaps:
        ds = counterMaps[counter]
        sds = dict(sorted(ds.items()))

        title = '%s-%s' % (device, counter)
        import matplotlib.pyplot as plt

        v = list(sds.values())
        dvl = [0] + [v[i+1] - v[i] for i in range(len(v)-1)]
        kl = list(sds.keys())
        plt.figure()
        plt.plot(kl, dvl)
        plt.title(title)
        plt.show()
        plt.savefig(title+'.png')
        plt.close()


def saveStateFile(stateFile, counterMaps):
    from pathlib import Path

    filepath = Path(stateFile)

    # rename file to backup, ignore if original does not exist
    try:
        filepath.rename(filepath.with_suffix('.bak'))
    except FileNotFoundError:
        pass
    with filepath.open('w') as file:
        fw = csv.DictWriter(file, fieldnames=stateFields)
        for c in counterMaps:
            cm = counterMaps[c]
            for h in cm:
                hm = cm[h]
                for entry in hm:
                    fw.writerow({'counter': c, 'device': h,
                                'date': entry, 'sample': hm[entry]})


def run():
    args = parseArgs()

    stateFile = args.stateFile[0]
    indir = args.input[0]
    outdir = args.output[0]

    # collect all input files
    # [f for f in os.listdir(indir) if f.endswith('.txt')]
    inFiles = glob.glob(indir + '/*.txt')
    print(indir + '/*.txt')
    print(inFiles)

    # make sure all snapshot files share the same prefix, the device name and followed by date
    # regex = '(?P<device>[^-]+)(-(?P<date>[^.]+))?\..*$'
    # for fn in args.snapshots:
    #     tm = re.match(regex, fn)
    #     if not tm:
    #         errExit('snapshot file does not have the right name format: %s' % fn)

    # build state
    counterMaps = buildState(stateFile)

    # add new samples if present
    for sf in inFiles:  # args.snapshots:
        # print('processing snapshot %s' %sf, file=sys.stderr)
        processSnapshot(counterMaps, sf)

    # trim if required
    if args.trim:
        trimState(counterMaps, args.trim[0])

    # plot state
    defaultMetrics = mapV6.keys()
    for m in (args.metrics or defaultMetrics):
        plotCounter(counterMaps, m, outdir)

    # if new sample, save new state with backup
    if inFiles:
        saveStateFile(stateFile, counterMaps)


if __name__ == '__main__':
    run()
