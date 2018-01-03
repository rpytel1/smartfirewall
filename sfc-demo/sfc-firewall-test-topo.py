#!/usr/bin/python

from subprocess import call
from mininetBase import SFC
from odlConfGeneration import sfcEncap
import sys


if __name__ == "__main__":

    sfc = SFC(sfcEncap.MAC_CHAIN, sys.argv[1])#(1) instantiate the SFC API with encapsulation type and ODL IP

    sw1 = sfc.addSw()                         #(2) Add the SFFs
    sw2 = sfc.addSw()
    sw3 = sfc.addSw()
    sw4 = sfc.addSw()

    h1 = sfc.addHost(sw1)                     #(3) Add host to be the src/dst of the chain
    h2 = sfc.addHost(sw1)
    h3 = sfc.addHost(sw1)
    h4 = sfc.addHost(sw1)

    sf1 = sfc.addSf('1', sw2, 'fw')           #(4) Add SFs with the SFF which it is connected and the SF type
    sf2 = sfc.addSf('2', sw3, 'dpi')
    sf3 = sfc.addSf('3', sw4, 'fw1')


    sfc.addLink(sw1, sw2)                     #(5) Add link among SFFs
    sfc.addLink(sw2, sw3)
    sfc.addLink(sw3, sw1)
    sfc.addLink(sw1, sw4)
    sfc.addLink(sw2, sw4)
    sfc.addLink(sw3, sw4)

    sfc.addGw(sw1)                            #(6) Add gateway at the end of the chain

    chain = ['fw', 'dpi', 'fw1']       #(7) The chain (list of SFs)

    sfc.addChain('c1', sw1, chain, True)
    # chain = ['fw1']                            #(8) Add the chain with name, classifier and the chain (list of SFs)
    # sfc.addChain('c2', sw1, chain, False)

    sfc.deployTopo()                          #(9) Deploy topology and chain configuration

