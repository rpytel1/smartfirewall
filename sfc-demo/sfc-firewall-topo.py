#!/usr/bin/python

from subprocess import call
from mininetBase import SFC
from odlConfGeneration import sfcEncap
import sys


class AclAddress:
    src = ""
    dst = ""

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst


if __name__ == "__main__":
    sfc = SFC(sfcEncap.MAC_CHAIN, sys.argv[1])  # (1) instantiate the SFC API with encapsulation type and ODL IP

    sw1 = sfc.addSw()  # (2) Add the SFFs
    sw2 = sfc.addSw()
    sw3 = sfc.addSw()

    h1 = sfc.addHost(sw1)  # (3) Add host to be the src/dst of the chain
    h2 = sfc.addHost(sw1)
    h3 = sfc.addHost(sw1)
    h4 = sfc.addHost(sw1)

    sf1 = sfc.addSf('1', sw2,
                    'fw')  # snort hacking         #(4) Add SFs with the SFF which it is connected and the SF type
    sf2 = sfc.addSf('2', sw3, 'fw1')  # snort protocols
    sf3 = sfc.addSf('3', sw2, 'dpi')

    sfc.addLink(sw1, sw2)  # (5) Add link among SFFs
    sfc.addLink(sw2, sw3)
    sfc.addLink(sw3, sw1)
    sfc.addGw(sw1)  # (6) Add gateway at the end of the chain

    # (7) The chains (list of SFs)



    chain = ['fw', 'fw1']
    aclUp = AclAddress("10.0.0.2/32", "10.0.0.4/32")
    sfc.addChain('c1', sw1, chain, "1", aclUp, True)  # (8) Add the chain with name, classifier and the chain (list of SFs)

    chain1 = ['fw1']
    aclUp1 = AclAddress("10.0.0.1/32", "10.0.0.4/32")
    sfc.addChain('c2', sw1, chain1, "2", aclUp1, True)

    #dummyChain = ['dpi']
    #aclUpDummy = AclAddress("10.0.0.0/29", "10.0.0.0/29")
    #sfc.addChain('c3', sw1, dummyChain, "3", aclUpDummy, True)

sfc.deployTopo()  # (9) Deploy topology and chain configuration
