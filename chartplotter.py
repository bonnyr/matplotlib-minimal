import matplotlib
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
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

mapRatioStats = {
    'sysIp6StatDropped': 'sysIp6StatRx',
    'sysIp6StatNbrPbqFullDropped': 'sysIp6StatRx',
    'sysIp6StatNbrUnreachableDropped': 'sysIp6StatRx',

    'sysIpStatDropped': 'sysIpStatRx',
    'sysIpStatNbrPbqFullDropped': 'sysIpStatRx',
    'sysIpStatNbrUnreachableDropped': 'sysIpStatRx',
}

mapInterfaceStatsBinding = {
    '1.2': '1.3',
    '1.4': '1.5',
}

EXPECTED_STAT_CNT = 52


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


def setCounter(counterMaps, c, h, d, s, acc=False):
    if c not in counterMaps:
        counterMaps[c] = {}
    cm = counterMaps[c]
    if not h in cm:
        cm[h] = {}
    hm = cm[h]
    if not d in hm:
        hm[d] = 0    

    v = 0
    if acc:
        v = hm[d]
    
    hm[d] = s + v
        


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

            m = re.match( '^.*::(?P<counter>[^.]+)\.0 = .*: (?P<sample>[0-9]+)$', l)
            mif = re.match( '^if_rx_tx (?P<if>[0-9]+\.[0-9]+) +(?P<rx_pkts>[0-9]+) +(?P<rx_drops>[0-9]+) +(?P<tx_pkts>[0-9]+) +(?P<tx_drops>[0-9]+)$', l)
            miqrx = re.match( '^iq_rx (?P<if>[0-9]+\.[0-9]+) +([0-9]+ +){5}(?P<drops>[0-9]+)$', l)
            miqtx = re.match( '^iq_tx (?P<if>[0-9]+\.[0-9]+) +([0-9]+ +){5}(?P<drops>[0-9]+)$', l)
            if m:
                statCnt += 1
                setCounter(counterMaps, m.group('counter'), device, date, int(m.group('sample')))
            if mif:
                setCounter(counterMaps, mif.group('if') + '-if_rx_drops', device, date, int(mif.group('rx_drops')), True)
                setCounter(counterMaps, mif.group('if') + '-if_tx_drops', device, date, int(mif.group('tx_drops')), True)
                setCounter(counterMaps, mif.group('if') + '-rx_pkts', device, date, int(mif.group('rx_pkts')), True)
                setCounter(counterMaps, mif.group('if') + '-tx_pkts', device, date, int(mif.group('tx_pkts')), True)
            if miqrx:
                setCounter(counterMaps, miqrx.group('if') + '-rx_drops', device, date, int(miqrx.group('drops')), True)
            if miqtx:
                setCounter(counterMaps, miqtx.group('if') + '-tx_drops', device, date, int(miqtx.group('drops')), True)

        if statCnt < EXPECTED_STAT_CNT:
            errExit('too few counters when processing file %s' % snapshotFile)


def getDiffFromMap(m, h):
    ds = m[h]
    sds = dict(sorted(ds.items()))

    v = list(sds.values())

    return v[len(v)-1] - v[len(v)-2]




def plotInterfaceStatsTable(fig, ax, ueRx, ueRxPkt, ueTx, ueTxPkt, intRx, intRxPkt, intTx, intTxPkt ):
    nrows = len(ueRx.keys())

    ax.set_xlim(0, 11)
    ax.set_ylim(0, nrows + 1)

    positions = [0, 1, 3, 5, 7, 9, 11]
    columns = ['-0-', 'Host', 'UE Rx', 'UE Tx ','Int Rx', 'Int Tx']

    colNdx = 0

    hs = sorted(ueRx.keys())
    for h in hs:
        ueRxDiff = getDiffFromMap(ueRx, h)
        ueTxDiff = getDiffFromMap(ueTx, h)
        intRxDiff = getDiffFromMap(intRx, h)
        intTxDiff = getDiffFromMap(intTx, h)

        ueRxPctDiff = getDiffFromMap(ueRxPkt, h)
        ueTxPctDiff = getDiffFromMap(ueTxPkt, h)
        intRxPctDiff = getDiffFromMap(intRxPkt, h)
        intTxPctDiff = getDiffFromMap(intTxPkt, h)

        # plot shape
        # -- Transformation functions
        DC_to_FC = ax.transData.transform
        FC_to_NFC = fig.transFigure.inverted().transform
        # -- Take data coordinates and transform them to normalized figure coordinates
        DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))
        # -- Add figure axes
        ax_point_1 = DC_to_NFC([2.25, 0.25])
        ax_point_2 = DC_to_NFC([2.75, 0.75])
        ax_width = abs(ax_point_1[0] - ax_point_2[0])
        ax_height = abs(ax_point_1[1] - ax_point_2[1])
        ax_coords = DC_to_NFC([0, nrows - colNdx - .75])
        plot_ax = fig.add_axes(
            [ax_coords[0], ax_coords[1], ax_width, ax_height]
        )
        plot_ax.plot([1],[1],'o-', color=colors[colNdx % 50])
        plot_ax.set_axis_off()


        ax.annotate(xy=(positions[1], nrows - colNdx - 0.5), s=h, ha='left', va='center')
        ax.annotate(xy=(positions[3]- 0.05, nrows - colNdx - 0.5), s='%d (%2.6f%%)' % (ueRxDiff, 0 if ueRxPctDiff == 0 else ueRxDiff / ueRxPctDiff * 100) , ha='right', va='center')
        ax.annotate(xy=(positions[4]- 0.05, nrows - colNdx - 0.5), s='%d (%2.6f%%)' % (ueTxDiff, 0 if ueTxPctDiff == 0 else ueTxDiff / ueTxPctDiff * 100), ha='right', va='center')
        ax.annotate(xy=(positions[5]- 0.05, nrows - colNdx - 0.5), s='%d (%2.6f%%)' % (intRxDiff, 0 if intRxPctDiff == 0 else intRxDiff / intRxPctDiff * 100), ha='right', va='center')
        ax.annotate(xy=(positions[6]- 0.05, nrows - colNdx - 0.5), s='%d (%2.6f%%)' % (intTxDiff, 0 if intTxPctDiff == 0 else intTxDiff / intTxPctDiff * 100), ha='right', va='center')


        colNdx += 1

    # -- Add column names
    for index, c in enumerate(columns):
            ax.annotate( xy=(positions[index], nrows + .05), s=columns[index], ha='left', va='bottom', weight='bold' )

    # Add dividing lines
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [nrows, nrows], lw=1.5, color='black', marker='', zorder=4)
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [0, 0], lw=1.5, color='black', marker='', zorder=4)
    for pos in range (1, len(positions), 2):
        ax.fill_between( x=[positions[pos],positions[pos+1]], y1=nrows, y2=0, color='lightgrey', alpha=0.5, zorder=-1, ec='None' )            
    for x in range(1, nrows):
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [x, x], lw=1.15, color='gray', ls=':', zorder=3 , marker='')

    for x in range(0, len(positions)):
        ax.plot([positions[x],positions[x]], [ax.get_ylim()[0], ax.get_ylim()[1]-1], lw=1.15, color='gray', zorder=3 , marker='')
    ax.set_axis_off()



def plotStats(name, m4, m6, tm, tm6, fig, ax,hdrs=None, posns=None):
    nrows = len(m4.keys())

    ax.set_xlim(0, 7.5)
    ax.set_ylim(0, nrows + 1)

    positions = [0, 1, 3.5, 5.5, 7.5]
    columns = ['-0-', 'Host', 'IPv4', 'IPv6']

    if hdrs:
        columns = hdrs

    # check if totals map is provided. Note assuming that if v4 is present, so will v6...
    if tm:
        ax.set_xlim(0, 10.5)
        positions = [0, 1, 4.5, 6.5, 7.5, 9.5, 10.5]
        columns = ['-0-', 'Host', 'IPv4', '%', 'IPv6', '%']

        # assume that if headers provided it has the right number of entries 
        if hdrs:
            columns = hdrs
            positions = posns

    colNdx = 0

    hs = sorted(m4.keys())
    for h in hs:
        d4 = getDiffFromMap(m4, h)
        d6 = getDiffFromMap(m6, h)
        td = None
        td6 = None
        if tm:
            td = getDiffFromMap(tm, h)
            td6 = getDiffFromMap(tm6, h)


        # plot shape
        # -- Transformation functions
        DC_to_FC = ax.transData.transform
        FC_to_NFC = fig.transFigure.inverted().transform
        # -- Take data coordinates and transform them to normalized figure coordinates
        DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))
        # -- Add figure axes
        ax_point_1 = DC_to_NFC([2.25, 0.25])
        ax_point_2 = DC_to_NFC([2.75, 0.75])
        ax_width = abs(ax_point_1[0] - ax_point_2[0])
        ax_height = abs(ax_point_1[1] - ax_point_2[1])
        ax_coords = DC_to_NFC([0, nrows - colNdx - .75])
        plot_ax = fig.add_axes(
            [ax_coords[0], ax_coords[1], ax_width, ax_height]
        )
        plot_ax.plot([1],[1],'o-', color=colors[colNdx % 50])
        plot_ax.set_axis_off()


        if not tm:
            ax.annotate(xy=(positions[1], nrows - colNdx - 0.5), s=h, ha='left', va='center')
            ax.annotate(xy=(positions[3]- 0.05, nrows - colNdx - 0.5), s=str(d4), ha='right', va='center')
            ax.annotate(xy=(positions[4]- 0.05, nrows - colNdx - 0.5), s=str(d6), ha='right', va='center')
        else:
            p4 = 0 if td == 0 else (d4 / td)
            p6 = 0 if td == 0 else (d6 / td6)
            ax.annotate(xy=(positions[1], nrows - colNdx - 0.5), s=h, ha='left', va='center')
            ax.annotate(xy=(positions[3]- 0.05, nrows - colNdx - 0.5), s=str(d4), ha='right', va='center')
            ax.annotate(xy=(positions[4]- 0.05, nrows - colNdx - 0.5), s='%2.2f' % p4, ha='right', va='center')
            ax.annotate(xy=(positions[5]- 0.05, nrows - colNdx - 0.5), s=str(d6), ha='right', va='center')
            ax.annotate(xy=(positions[6]- 0.05, nrows - colNdx - 0.5), s='%2.2f' % p6, ha='right', va='center')


        colNdx += 1

    # -- Add column names
    for index, c in enumerate(columns):
            ax.annotate( xy=(positions[index], nrows + .05), s=columns[index], ha='left', va='bottom', weight='bold' )

    # Add dividing lines
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [nrows, nrows], lw=1.5, color='black', marker='', zorder=4)
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [0, 0], lw=1.5, color='black', marker='', zorder=4)
    for pos in range (1, len(positions), 2):
        ax.fill_between( x=[positions[pos],positions[pos+1]], y1=nrows, y2=0, color='lightgrey', alpha=0.5, zorder=-1, ec='None' )            
    for x in range(1, nrows):
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [x, x], lw=1.15, color='gray', ls=':', zorder=3 , marker='')

    for x in range(0, len(positions)):
        ax.plot([positions[x],positions[x]], [ax.get_ylim()[0], ax.get_ylim()[1]-1], lw=1.15, color='gray', zorder=3 , marker='')
    ax.set_axis_off()

def plotFigure(name, m, ax):
    ax.set_title('%s - generated at %s' % (name, datetime.now().strftime('%Y%m%d-%H%M')))
    colNdx = 0

    hs = sorted(m.keys())
    for h in hs:
        ds = m[h]
        sds = dict(sorted(ds.items()))

        v = list(sds.values())
        dvl = [0] + [max(0, v[i+1] - v[i]) for i in range(len(v)-1)]
        kl = list(sds.keys())
        # print( 'plotting %s: %s' %(name, dvl))
        ax.tick_params(axis='x', rotation=45)
        ax.plot(kl, dvl, 'o-', label=h, color=colors[colNdx % 50])
        # ax.text(kl[-1], dvl[-1], h[len(h)-2:], bbox=dict(boxstyle="square,pad=0.3", fc="lightblue"))
        colNdx += 1


def plotCounter(counterMaps, counter, outdir):
    cm = counterMaps[counter]
    v6Counter = mapV6[counter]
    cm6 = counterMaps[v6Counter]


    tsm = None
    tsm6 = None
    if counter in mapRatioStats:
        tsm = counterMaps[mapRatioStats[counter]]
    if v6Counter in mapRatioStats:
        tsm6 = counterMaps[mapRatioStats[v6Counter]]


    fig = plt.figure()
    fig.set_size_inches(20, 10)

    gs = GridSpec(2, 2, width_ratios=[5, 2], height_ratios=[1, 1], left=0.05, right=0.95, wspace=0.25, hspace=0.25)
    ipv4Ax = fig.add_subplot(gs[0])
    statAx = fig.add_subplot(gs[1:])
    ipv6Ax = fig.add_subplot(gs[2])


    plotFigure(counter, cm, ipv4Ax)
    plotFigure(v6Counter, cm6, ipv6Ax)
    plotStats(v6Counter, cm, cm6, tsm, tsm6, fig, statAx)

    fn = os.path.join(outdir, counter + '-' +
                      datetime.now().strftime('%Y%m%d') + '.png')
    print('saving: ' + fn)
    plt.savefig(fn, dpi=100)
    plt.show()
    plt.close()


def plotInterfaceStats(counterMaps, outdir):
    ue_a = counterMaps['1.2-rx_drops']
    ue_s = counterMaps['1.3-rx_drops']
    int_a = counterMaps['1.4-rx_drops']
    int_s = counterMaps['1.5-rx_drops']

    ue_t_a = counterMaps['1.2-tx_drops']
    ue_t_s = counterMaps['1.3-tx_drops']
    int_t_a = counterMaps['1.4-tx_drops']
    int_t_s = counterMaps['1.5-tx_drops']

    if_ue_rx_a = counterMaps['1.2-rx_pkts']
    if_ue_rx_s = counterMaps['1.3-rx_pkts']
    if_ue_tx_a = counterMaps['1.2-tx_pkts']
    if_ue_tx_s = counterMaps['1.3-tx_pkts']
    if_int_rx_a = counterMaps['1.4-rx_pkts']
    if_int_rx_s = counterMaps['1.5-rx_pkts']
    if_int_tx_a = counterMaps['1.4-tx_pkts']
    if_int_tx_s = counterMaps['1.5-tx_pkts']

    ue = {k : {d : ue_a[k][d] + ue_s[k][d] for d in ue_a[k]} for k in ue_a.keys()}
    ue_t = {k : {d : ue_t_a[k][d] + ue_t_s[k][d] for d in ue_a[k]}  for k in ue_a.keys()}
    int = {k : {d : int_a[k][d] + int_s[k][d] for d in int_a[k]} for k in ue_a.keys()}
    int_t = {k: {d : int_t_a[k][d] + int_t_s[k][d] for d in int_a[k]} for k in ue_a.keys()}

    if_ue_rx = {k : {d : if_ue_rx_a[k][d] + if_ue_rx_s[k][d] for d in if_ue_rx_a[k]} for k in if_ue_rx_a.keys()}
    if_ue_tx = {k : {d : if_ue_tx_a[k][d] + if_ue_tx_s[k][d] for d in if_ue_tx_a[k]} for k in if_ue_tx_a.keys()}
    if_int_rx = {k : {d : if_int_rx_a[k][d] + if_int_rx_s[k][d] for d in if_int_rx_a[k]} for k in if_int_rx_a.keys()}
    if_int_tx = {k : {d : if_int_tx_a[k][d] + if_int_tx_s[k][d] for d in if_int_tx_a[k]} for k in if_int_tx_a.keys()}



    fig = plt.figure()
    fig.set_size_inches(20, 10)


    gs = GridSpec(4, 3, width_ratios=[4, 3, 1], height_ratios=[1, 1, 1, 1], left=0.05, right=0.98, wspace=0.05, hspace=0.15)
    ueAx = fig.add_subplot(gs[:1, :1])
    statAx = fig.add_subplot(gs[:, 1:4])
    ueTxAx = fig.add_subplot(gs[1:2, :1 ])
    intAx = fig.add_subplot(gs[2:3, :1])
    intTxAx = fig.add_subplot(gs[3:4, :1])


    plotFigure('ue side rx drops', ue, ueAx)
    plotFigure('internet side rx drops', int, intAx)
    plotFigure('ue side tx drops', ue_t, ueTxAx)
    plotFigure('internet side tx drops', int_t, intTxAx)


    plotInterfaceStatsTable(fig, statAx, ue, if_ue_rx, ue_t, if_ue_tx, int, if_int_rx, int_t, if_int_tx)

    fn = os.path.join(outdir, 'intf-' + datetime.now().strftime('%Y%m%d') + '.png')
    print('saving: ' + fn)
    plt.savefig(fn, dpi=100)
    plt.show()
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
    counterMaps = {}
    #buildState(stateFile)

    # add new samples if present
    for sf in inFiles:  # args.snapshots:
        # print('processing snapshot %s' %sf, file=sys.stderr)
        processSnapshot(counterMaps, sf)

    # trim if required
    if args.trim:
        trimState(counterMaps, args.trim[0])

    # plot stats
    defaultMetrics = mapV6.keys()
    for m in (args.metrics or defaultMetrics):
        plotCounter(counterMaps, m, outdir)

    # plot inteface stats
    plotInterfaceStats(counterMaps, outdir)

    # if new sample, save new state with backup
    if inFiles:
        saveStateFile(stateFile, counterMaps)


if __name__ == '__main__':
    run()
