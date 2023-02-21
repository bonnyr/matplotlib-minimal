import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os,sys
from datetime import datetime
from dateutil import parser
import csv
import argparse
import re
import glob


stateFields = ['counter','device', 'date', 'sample']

mapV6 = {
'sysIpStatResetStats' : 'sysIp6StatResetStats',
'sysIpStatTx' : 'sysIp6StatTx',
'sysIpStatRx' : 'sysIp6StatRx',
'sysIpStatDropped' : 'sysIp6StatDropped',
'sysIpStatRxFrag' : 'sysIp6StatRxFrag',
'sysIpStatRxFragDropped' : 'sysIp6StatRxFragDropped',
'sysIpStatTxFrag' : 'sysIp6StatTxFrag',
'sysIpStatTxFragDropped' : 'sysIp6StatTxFragDropped',
'sysIpStatReassembled' : 'sysIp6StatReassembled',
'sysIpStatErrCksum' : 'sysIp6StatErrCksum',
'sysIpStatErrLen' : 'sysIp6StatErrLen',
'sysIpStatErrMem' : 'sysIp6StatErrMem',
'sysIpStatErrRtx' : 'sysIp6StatErrRtx',
'sysIpStatErrProto' : 'sysIp6StatErrProto',
'sysIpStatErrOpt' : 'sysIp6StatErrOpt',
'sysIpStatErrReassembledTooLong' : 'sysIp6StatErrReassembledTooLong',
'sysIpStatNbrPbqFullDropped' : 'sysIp6StatNbrPbqFullDropped',
'sysIpStatNbrUnreachableDropped' : 'sysIp6StatNbrUnreachableDropped',
'sysIpStatMcastTx' : 'sysIp6StatMcastTx',
'sysIpStatMcastRx' : 'sysIp6StatMcastRx',
'sysIpStatErrMcastRpf' : 'sysIp6StatErrMcastRpf',
'sysIpStatErrMcastWrongIf' : 'sysIp6StatErrMcastWrongIf',
'sysIpStatErrMcastNoRoute' : 'sysIp6StatErrMcastNoRoute',
'sysIpStatErrMcastRouteLookupTimeout' : 'sysIp6StatErrMcastRouteLookupTimeout',
'sysIpStatErrMcastMaxPendingPackets' : 'sysIp6StatErrMcastMaxPendingPackets',
'sysIpStatErrMcastMaxPendingRoutes' : 'sysIp6StatErrMcastMaxPendingRoutes',    
}

EXPECTED_STAT_CNT = 52

def errExit(err):
    print(err)
    sys.exit(-1)


def parseArgs():
    parser = argparse.ArgumentParser(description='Maintain counter snapshot and plot them')
    parser.add_argument('stateFile', metavar='state', type=str, nargs=1, help='path to state file. Required')
    parser.add_argument('input', metavar='input', type=str, nargs=1, help='path to input directory containing SNMP counter data. Required')
    parser.add_argument('output', metavar='output', type=str, nargs=1, help='path to output directory where generated graphs are stored. Required')
    parser.add_argument('-m', '--metric', dest='metrics', action='append', help='name of counter to plot. Optional. If no counters are specified, all counters are plotted')
    parser.add_argument('-t', '--trim', dest='trim', type=int, nargs=1)

    return parser.parse_args()


def setCounter(counterMaps, c, h, d, s):
    if c not in counterMaps:
        counterMaps[c] = {}
    cm = counterMaps[c]
    if not h in cm:
        cm[h] = {}             
    hm = cm[h] 
    hm[d]=s               


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
    m  = re.match('(.*/)?(?P<device>[^-]+)-((?P<date>.*)(-(?P<time>.*))?)\..*$', snapshotFile)
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

            m = re.match('^.*::(?P<counter>[^.]+)\.0 = .*: (?P<sample>[0-9]+)$', l)
            if not m:
                continue

            # if not device:
            #     errExit('stat line encountered but hostname is not present in file %s' %snapshotFile)

            statCnt += 1
            setCounter(counterMaps, m.group('counter'), device, date, int(m.group('sample')))
        
        if statCnt < EXPECTED_STAT_CNT:
            errExit('too few counters when processing file %s' %snapshotFile)
            

def plotCounter(counterMaps, counter, outdir):
    cm = counterMaps[counter]
    v6Counter = mapV6[counter]
    cm6 = counterMaps[v6Counter]

    fig, axis = plt.subplots(2)
    fig.set_size_inches(20,10)
    fig.tight_layout(pad=8)
    plt.subplots_adjust(right=0.7, left=0.05)

    colmap = plt.get_cmap('gist_rainbow')

    def plotFigure(name, m, row):
        axis[row].set_title('%s - generated at %s' % (name, datetime.now().strftime('%Y%m%d-%H%M')))
        colNdx=0
        for h in m:
            ds = m[h]
            sds = dict(sorted(ds.items()))

            v = list(sds.values())
            dvl = [0] +[ v[i+1] - v[i] for i in range(len(v)-1)]
            kl = list(sds.keys())
            # print( 'plotting %s: %s' %(name, dvl))
            axis[row].tick_params(axis='x', rotation=45)
            axis[row].plot(kl, dvl, 'o-', label=h, color=colmap(1.*colNdx/len(m)))
            colNdx += 1

        if row == 0:
            axis[row].legend(bbox_to_anchor=(1.04, 1), loc="upper left")#, ncol=int(len(m)/30)+1)

    plotFigure(counter, cm, 0)
    plotFigure(v6Counter, cm6, 1)

    fn = os.path.join(outdir, counter + '-' + datetime.now().strftime('%Y%m%d') + '.png')
    print('saving: ' + fn)
    plt.savefig(fn, dpi=100)
    plt.show()
    plt.close()

def plotCounters(counterMaps, device):
    for counter in counterMaps:
        ds = counterMaps[counter]
        sds = dict(sorted(ds.items()))

        title = '%s-%s' %(device, counter)
        import matplotlib.pyplot as plt


        v = list(sds.values())
        dvl = [0] +[ v[i+1] - v[i] for i in range(len(v)-1)]
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
                    fw.writerow({'counter': c, 'device': h, 'date': entry, 'sample': hm[entry]})

def run():
    args = parseArgs()

    stateFile = args.stateFile[0]
    indir = args.input[0]
    outdir = args.output[0]


    # collect all input files  
    inFiles = glob.glob(indir + '/*.txt') # [f for f in os.listdir(indir) if f.endswith('.txt')]
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
    for sf in inFiles: #args.snapshots:
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