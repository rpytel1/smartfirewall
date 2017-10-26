/*
 * Copyright (c) 2016 Ericsson India Global Services Pvt Ltd. and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */

package org.opendaylight.smartfirewall.impl;

import org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.smartfirewall.rev150105.access.list.AccessListEntry;
import org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.smartfirewall.rev150105.access.list.access.list.entry.actions.PacketHandling;

public class FlowData {


    private String dstIpAddress = null;
    private int dstPrefix;
    private String srcIpAddress = null;
    private int srcPrefix;
    private PacketHandling packetHandlingAction = null;
    private String nodeId = null;
    private String ruleName = null;
    private long etherType = 0L;
    private int priority = 0;
    private int hardTimeout = 0;
    private int idleTimeout = 0;

    public FlowData(AccessListEntry entry) {

        this.etherType = FirewallConstants.ETH_TYPE ;
        // TODO change the priority accordingly
        this.priority = FirewallConstants.FLOW_PRIORITY ;
        this.hardTimeout = FirewallConstants.DEFAULT_TIMEOUT_VALUE ;
        this.idleTimeout = FirewallConstants.DEFAULT_TIMEOUT_VALUE ;
        String dstIpAddressTmp = entry.getMatches().getDestinationIpv4Network().getValue();
        String srcIpAddressTmp = entry.getMatches().getSourceIpv4Network().getValue();
        String [] parts = dstIpAddressTmp
                .split(FirewallConstants.SUBNET_MASK_SEPARATOR ) ;
        this.setDstIpAddress(parts[0]) ;
        this.dstPrefix = (parts.length == 1) ? 0 : Integer.parseInt(parts[1]);
        parts = srcIpAddressTmp
                .split(FirewallConstants.SUBNET_MASK_SEPARATOR ) ;
        this.setSrcIpAddress(parts[0]);
        this.srcPrefix = (parts.length == 1) ? 0 : Integer.parseInt(parts[1]);
        this.ruleName = entry.getRuleName();
        this.setNodeId(entry.getNodeId());
        this.setPacketHandlingAction(entry.getActions().getPacketHandling());
    }

    public PacketHandling getPacketHandlingAction() {
        return packetHandlingAction;
    }

    public String getSrcIpAddress() {
        return srcIpAddress;
    }

    public int getSrcPrefix() {
        return srcPrefix;
    }

    public void setSrcIpAddress(String srcIpAddress) {
        this.srcIpAddress = srcIpAddress;
    }

    public void setSrcPrefix(int srcPrefix) {
        this.srcPrefix = srcPrefix;
    }


    public int getDstPrefix() {
        return dstPrefix;
    }

    public String getDstIpAddress() {
        return dstIpAddress;
    }

    public void setDstIpAddress(String dstIpAddress) {
        this.dstIpAddress = dstIpAddress;
    }

    public String getNodeId() {
        return nodeId;
    }

    public void setNodeId(String nodeId) {
        this.nodeId = nodeId;
    }

    public String getRuleName() {
        return ruleName;
    }

    public int getPriority() {
        return priority;
    }

    public int getHardTimeout() {
        return hardTimeout;
    }

    public int getIdleTimeout() {
        return idleTimeout;
    }

    public void setPacketHandlingAction(PacketHandling packetHandlingAction) {
        this.packetHandlingAction = packetHandlingAction;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof FlowData)) return false;

        FlowData flowData = (FlowData) o;

        if (etherType != flowData.etherType) return false;
        if (priority != flowData.priority) return false;
        if (hardTimeout != flowData.hardTimeout) return false;
        if (idleTimeout != flowData.idleTimeout) return false;
        if (!dstIpAddress.equals(flowData.dstIpAddress)) return false;
        if (!nodeId.equals(flowData.nodeId)) return false;
        return ruleName.equals(flowData.ruleName);

    }

    @Override
    public int hashCode() {
        int result = dstIpAddress.hashCode();
        result = 31 * result + nodeId.hashCode();
        result = 31 * result + ruleName.hashCode();
        result = 31 * result + (int) (etherType ^ (etherType >>> 32));
        result = 31 * result + priority;
        result = 31 * result + hardTimeout;
        result = 31 * result + idleTimeout;
        return result;
    }

    @Override
    public String toString() {
        return "FlowData{" +
                ", dstIpAddress='" + dstIpAddress + '\'' +
                ", nodeList=" + nodeId +
                ", ruleName='" + ruleName + '\'' +
                ", etherType=" + etherType +
                ", priority=" + priority +
                ", hardTimeout=" + hardTimeout +
                ", idleTimeout=" + idleTimeout +
                '}';
    }

}
