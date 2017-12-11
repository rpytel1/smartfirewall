#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.link import Intf
from mininet.clean import Cleanup
from mininet.log import setLogLevel, info
from subprocess import call
import subprocess
from odlConfGeneration import odlConf, sfcEncap
import re
import os
import time


class SFC:

    YOUR_CONTROLLER_IP = ''
    net = None
    callBackConfs = {'host': [], 'sf': [], 'sw': [], 'chain':[] }
    odl = None
    topo = None
    ovsUuid = None
    sffs = []
    hosts = []
    sfs = []
    popens = {}


    def deployTopo(self):

        self.topo = self.net.start()
        time.sleep(1)
        # clean previous rules
        self.odl.clean(self.callBackConfs['chain'], self.callBackConfs['sw'])
        time.sleep(1)
        # self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.DISABLE_STATISTICS, self.odl.disableStatistics(), True)


        self.deploySwConf()
        self.deployHostConf()
        self.deploySfConf()

        self.deployODLConf()

        #deploy chain
        self.deploySfc()

        self.disableOffLoadFromIfaces()

        CLI(self.net)
        self.odl.clean(self.callBackConfs['chain'], self.callBackConfs['sw'])
        self.cleanProcess()
        Cleanup()

    def __init__(self, encap, controller):
        self.odl = odlConf(encap)
        self.odl.readParameters()
        call('mn --clean', shell=True)
        time.sleep(1)

        self.YOUR_CONTROLLER_IP = controller

        call('ovs-vsctl set-manager tcp:%s:6640' %self.YOUR_CONTROLLER_IP, shell=True)

        self.ovsUuid = self.getOvsdbId()

        self.net = Mininet(controller=None)
        self.net.addController('c0', controller=RemoteController, ip=self.odl.controller, port=6633)

    def addHost(self, sw):

        num = str(len(self.sfs) + 1)
        host = self.net.addHost("h%s" % (num))

        self.sfs.append(host)
        self.net.addLink(host, sw)
        hostConf = {}
        hostConf[host] = {}
        hostConf[host]['IP'] = '10.0.0.'+(num)
        hostConf[host]['MAC'] = '00:00:00:00:00:0%s' %(num)
        self.callBackConfs['host'].append(hostConf)
        return host


    def addSf(self, num, sw, type):
        sf = self.net.addHost("sf%s" % (num))
        link = self.net.addLink(sf, sw)
        ports = []
        ports.append(sw.ports[link.intf2])
        sfConf = {}
        sfConf[sf] = {}
        sfConf[sf]['IP'] = []
        sfConf[sf]['MAC'] = []
        sfConf[sf]['IP'].append('10.0.0.1%s' % (num))
        sfConf[sf]['MAC'].append('00:00:00:00:00:1%s' % (num))
        sfConf[sf]['iface'] = []
        sfConf[sf]['iface'].append(link.intf1)
        tag = 300 + int(num)
        sfConf[sf]['CMD'] = []

        #for Vlan sfc encapsulation sf interfaces are tagged to spesific VLAN IDs
        if self.odl.sfcEncap == sfcEncap.VLAN:
            sfConf[sf]['CMD'].append("vconfig add sf%s-eth0 %s" % (num, str(tag)))
            sfConf[sf]['CMD'].append("ip link set up sf%s-eth0.%s" % (num, str(tag)))
            sfConf[sf]['CMD'].append("python ./functions/sf_dummy.py sf%s-eth0.%s %s > /tmp/sf%s.out  &" % (num, str(tag), str(tag), num))
        elif self.odl.sfcEncap == sfcEncap.MAC_CHAIN:
            sfConf[sf]['CMD'].append("python ./functions/sf_dummy.py sf%s-eth0 > /tmp/sf%s.out  &" % (num, num))

        sfConf[sf]['CONF'] = self.odl.sfConf(sf.name, num, type, sfConf[sf]['IP'], sw.name, tag, sfConf[sf]['MAC'], ports, self.getODLSwConf(sw))
        self.callBackConfs['sf'].append(sfConf)

        return sf

    def addSnort(self, num, sw, type):
        sf = self.net.addHost("snort%s" % (num))
        ports = []
        link1 = self.net.addLink(sf, sw)
        ports.append(sw.ports[link1.intf2])

        link2 = self.net.addLink(sf, sw)
        ports.append(sw.ports[link2.intf2])

        sfConf = {}
        sfConf[sf] = {}
        sfConf[sf]['IP'] =[]
        sfConf[sf]['IP'].append('10.0.0.1%s' % (num))
        sfConf[sf]['IP'].append('10.0.0.2%s' % (num))
        sfConf[sf]['MAC'] = []
        sfConf[sf]['MAC'].append('00:00:00:00:00:1%s' % (num))
        sfConf[sf]['MAC'].append('00:00:00:00:00:2%s' % (num))
        sfConf[sf]['iface'] = []
        sfConf[sf]['iface'].append(link1.intf1)
        sfConf[sf]['iface'].append(link2.intf1)

        tag = 300 + int(num)
        sfConf[sf]['CMD'] = []

        if self.odl.sfcEncap == sfcEncap.VLAN:
            sfConf[sf]['CMD'].append("vconfig add snort%s-eth0 %s" % (num, str(tag)))
            sfConf[sf]['CMD'].append("ip link set up snort%s-eth0.%s" % (num, str(tag)))

            sfConf[sf]['CMD'].append("vconfig add snort%s-eth1 %s" % (num, str(tag)))
            sfConf[sf]['CMD'].append("ip link set up snort%s-eth1.%s" % (num, str(tag)))
            sfConf[sf]['CMD'].append("/usr/sbin/snort --daq afpacket -Q -K ascii -c /etc/snort/snort.conf -i snort%s-eth0.%s:snort%s-eth1.%s -l /tmp/ > /tmp/snort%s.out 2>&1 &"
                % (num, str(tag), num, str(tag), num))
        elif self.odl.sfcEncap == sfcEncap.MAC_CHAIN:
            sfConf[sf]['CMD'].append("/usr/sbin/snort --daq afpacket -Q -K ascii -c /etc/snort/snort.conf -i snort%s-eth0:snort%s-eth1 -l /tmp/ > /tmp/snort%s.out 2>&1 &"
                % (num, num, num))


        sfConf[sf]['CONF'] = self.odl.sfConf(sf.name, num, type, sfConf[sf]['IP'], sw.name, tag, sfConf[sf]['MAC'],
                                             ports, self.getODLSwConf(sw))

        sfConf[sf]['TYPE'] = self.odl.sfType(sfConf[sf]['CONF']['service-function'][0]['type'])

        self.callBackConfs['sf'].append(sfConf)

        return sf


    def addSw(self):
        num = str(len(self.sffs) + 1)
        sw = self.net.addSwitch('SFF%s' %num)

        self.sffs.append(sw)

        swConf = {}
        swConf[sw] = {}
        swConf[sw]['CMD'] = []
        swConf[sw]['CMD'].append('ovs-vsctl set bridge %s protocols=OpenFlow13'%(sw.name))

        swConf[sw]['CONF'] = self.odl.sffConfBase(sw.name, num, self.ovsUuid)
        self.callBackConfs['sw'].append(swConf)
        return sw

    def addGw(self, sw):
        gw = self.net.addHost('gw')
        link = self.net.addLink(gw, sw)
        gwConf = {}
        gwConf[gw] = {}
        gwConf[gw]['iface'] = []
        gwConf[gw]['IP'] = []
        gwConf[gw]['MAC'] = []
        gwConf[gw]['IP'].append('10.0.0.30')
        gwConf[gw]['MAC'].append('00:00:00:00:00:FE')
        gwConf[gw]['iface'].append(link.intf1)
        gwConf[gw]['CMD'] = []
        gwConf[gw]['CMD'].append("python ./functions/gw.py gw-eth0 > /tmp/gw.out &")

        # set chain termination point to mac chain
        if self.odl.sfcEncap == sfcEncap.MAC_CHAIN:
            self.odl.appendSffTermination(self.getODLSwConf(sw), sw.ports[link.intf2], '9', gwConf[gw]['MAC'][0])

        self.callBackConfs['sf'].append(gwConf)

    def addLink(self, sw1, sw2):
        link = self.net.addLink(sw1, sw2)
        portSw2 = sw2.ports[link.intf2]
        portSw1 = sw1.ports[link.intf1]
        self.odl.appendSffConf(self.getODLSwConf(sw1), portSw1, str(self.sffs.index(sw1) +1), self.getODLSwConf(sw2), portSw2, str(self.sffs.index(sw2) +1))

    def addChain(self, name, sw1, chain, id, aclAddress, addReverse):

        chainConf = {}
        chainConf[name] = {}
        chainConf[name]['sfc'] = self.odl.setChain(name, chain)

        aclName1 = "acl.up" + id
        aclName2 = "acl.down" + id
        aclName3 = "acl.tcp.up" + id
        aclName4 = "acl.tcp.down" + id

        chainConf[name]['scf1'] = self.odl.setClassifier1(sw1.name, aclName1)
        if addReverse:
            chainConf[name]['scf2'] = self.odl.setClassifier2(sw1.name, aclName2)

        chainConf[name]['scf3'] = self.odl.setClassifier1(sw1.name, aclName3)
        if addReverse:
            chainConf[name]['scf4'] = self.odl.setClassifier2(sw1.name, aclName4)

        if addReverse:
            chainConf[name]['sfp'] = self.odl.setChainPath(name, chainConf[name]['scf1']['service-function-classifier']['name'],
                                               chainConf[name]['scf2']['service-function-classifier']['name'])
        else:
            chainConf[name]['sfp'] = self.odl.setAssymetricChainPath(name, chainConf[name]['scf1']['service-function-classifier']['name'])
        chainConf[name]['rsp'] = self.odl.rederedRPC(chainConf[name]['sfp']['service-function-path']['name'])

        chainConf[name]['acl1'] = self.odl.aclRuleUp(chainConf[name]['rsp']['input']['name'], aclName1, aclAddress)
        chainConf[name]['acl3'] = self.odl.aclRuleUpTcp(chainConf[name]['rsp']['input']['name'], aclName3, aclAddress)

        if addReverse:
            chainConf[name]['acl2'] = self.odl.aclRuleDown(chainConf[name]['rsp']['input']['name'], aclName2, aclAddress)
            chainConf[name]['acl4'] = self.odl.aclRuleDownTcp(chainConf[name]['rsp']['input']['name'], aclName4, aclAddress)


        self.callBackConfs['chain'].append(chainConf)

    def getODLSwConf(self, sff):
        for sw in self.callBackConfs['sw']:
            for swTopo, conf in sw.iteritems():
                if swTopo == sff:
                    return conf['CONF']
        return None

    def deployHostConf(self):
        for host in self.callBackConfs['host']:
            for hostTopo, conf in host.iteritems():
                hostTopo.setIP(conf['IP'])
                hostTopo.setMAC(conf['MAC'])
                hostTopo.cmd("/usr/sbin/sshd")
                self.popens[hostTopo] = []
                if hostTopo.name == 'h2':
                    hostTopo.cmd("pushd /var/www/html/; python -m SimpleHTTPServer 5040 > /tmp/server1.out 2>&1 &")
                    self.popens[hostTopo].append(int(hostTopo.cmd('echo $!')))
                    hostTopo.cmd("pushd /var/www/html/; python -m SimpleHTTPServer 5050 > /tmp/server2.out 2>&1 &")
                    self.popens[hostTopo].append(int(hostTopo.cmd('echo $!')))

    def deploySfConf(self):
        for sf in self.callBackConfs['sf']:
            for sfTopo, conf in sf.iteritems():
                for ip, iface in zip(conf['IP'], conf['iface']):
                    print ip
                    print iface
                    sfTopo.setIP(ip, intf=iface)
                for mac, iface in zip(conf['MAC'], conf['iface']):
                    sfTopo.setMAC(mac, intf=iface)
                self.popens[sfTopo] = []
                for cmd in conf['CMD']:
                    print cmd
                    sfTopo.cmd(cmd)
                    pid = sfTopo.cmd('echo $!')
                    if  bool(pid.strip()):
                        self.popens[sfTopo].append(int(pid))
                if sfTopo.name is not 'gw':
                    print "post odl conf:"
                    if conf['CONF']['service-function'][0]['type'] == "service-function-type:ips" or  conf['CONF']['service-function'][0]['type'] == "service-function-type:ips1":
                        self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_FUNCTION_TYPE, conf['TYPE'], True)
                    self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_FUNCTION, conf['CONF'], True)



    def deploySwConf(self):
        for sw in self.callBackConfs['sw']:
            for swTopo, conf in sw.iteritems():
                print swTopo.name
                for cmd in conf['CMD']:
                    print cmd
                    call(cmd, shell=True)

    def deployODLConf(self):
        for sw in self.callBackConfs['sw']:
            for swTopo, conf in sw.iteritems():
                self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_FUNCTION_FORWARDER, conf['CONF'], True)

    def deploySfc(self):
        for chain in self.callBackConfs['chain']:
            for chainName, conf in chain.iteritems():
                self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_FUNCTION_CHAIN, conf['sfc'], True)
                self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_FUNCTION_PATH, conf['sfp'], True)
                self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.ACCESS_CONTROL_LIST, conf['acl1'], True)
                self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.ACCESS_CONTROL_LIST, conf['acl3'], True)
                if 'acl2' in conf:
                    self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.ACCESS_CONTROL_LIST, conf['acl2'], True)
                if 'acl4' in conf:
                    self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.ACCESS_CONTROL_LIST, conf['acl4'], True)

                self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_RENDERED_PATH, conf['rsp'], True)
                self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_CLASSIFICATION_FUNTION, conf['scf1'], True)
                self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_CLASSIFICATION_FUNTION, conf['scf3'], True)
                if 'scf2' in conf:
                    self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_CLASSIFICATION_FUNTION, conf['scf2'], True)
                if 'scf4' in conf:
                    self.odl.post(self.odl.controller, self.odl.DEFAULT_PORT, self.odl.SERVICE_CLASSIFICATION_FUNTION, conf['scf4'], True)

        scf = conf['scf1']['service-function-classifier']['scl-service-function-forwarder'][0]['name']
        print scf
        if self.odl.sfcEncap == sfcEncap.MAC_CHAIN:
            call('ovs-ofctl -OOpenFlow13 add-flow %s priority=99,actions=normal' % (scf), shell=True)  # normal traffic from no chain

    def disableOffLoadFromIfaces(self):
        p = subprocess.Popen(['tcpdump', '-D'], stdout=subprocess.PIPE,  stderr = subprocess.PIPE)
        out, err = p.communicate()
        ifaces = out.split("\n")
        for iface in ifaces:
            if re.match("[0-9]{1,2}\.SFF.+", iface):
                foundIface = iface.split(".")[1]
                call('ethtool --offload  %s  rx off  tx off' %foundIface, stdout=None, shell=True)



    def cleanProcess(self):
        for cmds in self.popens.values():
            for cmd in cmds:
                print cmd
                call('kill %d' %(cmd), shell=True) #SIGINT

    def getOvsdbId(self):
        output1 = subprocess.check_output('ovs-vsctl show', shell=True,  universal_newlines=True, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
        res = output1.split("\n")
        return res[0]



