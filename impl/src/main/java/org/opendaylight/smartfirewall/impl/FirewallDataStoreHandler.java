/*
 * Copyright (c) 2016 Ericsson India Global Services Pvt Ltd. and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */

package org.opendaylight.smartfirewall.impl;


import org.opendaylight.controller.md.sal.binding.api.DataBroker;
import org.opendaylight.controller.md.sal.binding.api.DataObjectModification;
import org.opendaylight.genius.mdsalutil.*;
import org.opendaylight.genius.mdsalutil.actions.ActionOutput;
import org.opendaylight.genius.mdsalutil.instructions.InstructionApplyActions;
import org.opendaylight.genius.mdsalutil.interfaces.IMdsalApiManager;
import org.opendaylight.genius.mdsalutil.matches.MatchEthernetType;
import org.opendaylight.genius.mdsalutil.matches.MatchIpv4Destination;
import org.opendaylight.yang.gen.v1.urn.ietf.params.xml.ns.yang.ietf.inet.types.rev130715.Ipv4Prefix;
import org.opendaylight.yang.gen.v1.urn.ietf.params.xml.ns.yang.ietf.inet.types.rev130715.Uri;
import org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.smartfirewall.rev150105.AccessList;
import org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.smartfirewall.rev150105.access.list.AccessListEntry;
import org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.smartfirewall.rev150105.access.list.access.list.entry.actions.packet.handling.Permit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;

public class FirewallDataStoreHandler {

    private static final Logger LOG = LoggerFactory.getLogger(FirewallDataStoreHandler.class);

    private DataBroker dataBroker;
    private IMdsalApiManager mdsalApiManager;

    public FirewallDataStoreHandler(DataBroker broker, IMdsalApiManager mdsalApiManager) {
        this.dataBroker = broker;
        this.mdsalApiManager = mdsalApiManager;
    }

    public void installFlow(DataObjectModification<AccessList> change) {
        LOG.info(" installflow with data {} ", change);

        AccessList accList = change.getDataAfter();

        List<AccessListEntry> entries = accList.getAccessListEntry();
        for (AccessListEntry entry : entries) {
            FlowData flowData = new FlowData(entry);
            populateMDsalUtilWay(flowData);
        }
    }

    private void populateMDsalUtilWay(FlowData flowData) {
            FlowEntity flowEntity = getFlowEntity(flowData, flowData.getNodeId());
            mdsalApiManager.installFlow(flowEntity);
        if (flowData.getPacketHandlingAction() instanceof Permit) {
            mdsalApiManager.installFlow(getDownLinkFlowEntity(flowData, flowData.getNodeId()));
        }
        LOG.info("SampleApp default flow is installed successfully in node {}.", flowData.getNodeId());
    }

    private String getFlowRef(final String dstIp, final String ruleName) {
        return new StringBuilder(256).append(FirewallConstants.FLOWID_PREFIX)
                .append(FirewallConstants.RULENAME_SEPARATOR).append(ruleName).append(FirewallConstants.RULENAME_SEPARATOR)
                .append(FirewallConstants.FLOWID_SEPARATOR).append(dstIp).toString();
    }

    private String getNodeId(String nodeString) {
        String[] parts = nodeString
                .split(FirewallConstants.RULENAME_SEPARATOR);
        return parts[1];
    }

    private FlowEntity getFlowEntity(FlowData flowBuilder, String nodeId) {
        FlowEntityBuilder flowEntityBuilder = new FlowEntityBuilder().setDpnId(new BigInteger(getNodeId(nodeId)));
        long outPortNum = 2L;
        String flowId = getFlowRef(flowBuilder.getDstIpAddress(), flowBuilder.getRuleName());
        BigInteger cookieValue = FirewallConstants.COOKIE_SAMPLEAPP_BASE.add(new BigInteger("0120000", 16)).add(BigInteger.valueOf(10L));
        List<MatchInfo> mkMatches = new ArrayList<MatchInfo>();
        mkMatches.add(new MatchEthernetType(new Long(0x0800L)));
        if (flowBuilder.getDstPrefix() != 0) {
            mkMatches.add(new MatchIpv4Destination(new Ipv4Prefix(flowBuilder.getDstIpAddress()+"/"+Integer.toString(flowBuilder.getDstPrefix()))));
        }
        List<InstructionInfo> mkInstructions = new ArrayList<InstructionInfo>();
        List<ActionInfo> listActionInfo = new ArrayList<ActionInfo>();
        if (flowBuilder.getPacketHandlingAction() instanceof Permit) {
            listActionInfo.add(new ActionOutput(new Uri(Long.toString(outPortNum))));
            flowEntityBuilder.setPriority(5);
        } else {
            flowEntityBuilder.setPriority(4);
        }
        mkInstructions.add(new InstructionApplyActions(listActionInfo));
        flowEntityBuilder.setCookie(cookieValue);
        flowEntityBuilder.setFlowId(flowId);
        flowEntityBuilder.setFlowName(FirewallConstants.DEFAULT_RULE_NAME);
        flowEntityBuilder.setHardTimeOut(flowBuilder.getHardTimeout());
        flowEntityBuilder.setIdleTimeOut(flowBuilder.getIdleTimeout());
        flowEntityBuilder.setInstructionInfoList(mkInstructions);
        flowEntityBuilder.setMatchInfoList(mkMatches);
        flowEntityBuilder.setSendFlowRemFlag(false);
        flowEntityBuilder.setStrictFlag(false);
        flowEntityBuilder.setTableId((short) 0);
        flowEntityBuilder.setDpnId(new BigInteger(getNodeId(nodeId)));
        return flowEntityBuilder.build();
    }

    private FlowEntity getDownLinkFlowEntity(FlowData flowBuilder, String nodeId) {
        FlowEntityBuilder flowEntityBuilder = new FlowEntityBuilder().setDpnId(new BigInteger(getNodeId(nodeId)));
        long intPortNum = 1L;
        String flowId = getFlowRef(flowBuilder.getSrcIpAddress(), "DOWNLINKPERMIT");
        BigInteger cookieValue = FirewallConstants.COOKIE_SAMPLEAPP_BASE.add(new BigInteger("0230000", 16)).add(BigInteger.valueOf(20L));
        List<MatchInfo> mkMatches = new ArrayList<MatchInfo>();
        mkMatches.add(new MatchEthernetType(new Long(0x0800L)));
        if (flowBuilder.getSrcPrefix() != 0) {
            mkMatches.add(new MatchIpv4Destination(new Ipv4Prefix(flowBuilder.getSrcIpAddress()+"/"+Integer.toString(flowBuilder.getSrcPrefix()))));
        }
        List<InstructionInfo> mkInstructions = new ArrayList<InstructionInfo>();
        List<ActionInfo> listActionInfo = new ArrayList<ActionInfo>();
        listActionInfo.add(new ActionOutput(new Uri(Long.toString(intPortNum))));
        flowEntityBuilder.setPriority(5);
        mkInstructions.add(new InstructionApplyActions(listActionInfo));
        flowEntityBuilder.setCookie(cookieValue);
        flowEntityBuilder.setFlowId(flowId);
        flowEntityBuilder.setFlowName("DOWNLINKPERMITFLOW");
        flowEntityBuilder.setHardTimeOut(flowBuilder.getHardTimeout());
        flowEntityBuilder.setIdleTimeOut(flowBuilder.getIdleTimeout());
        flowEntityBuilder.setInstructionInfoList(mkInstructions);
        flowEntityBuilder.setMatchInfoList(mkMatches);
        flowEntityBuilder.setSendFlowRemFlag(false);
        flowEntityBuilder.setStrictFlag(false);
        flowEntityBuilder.setTableId((short) 0);
        flowEntityBuilder.setDpnId(new BigInteger(getNodeId(nodeId)));
        return flowEntityBuilder.build();
    }
}
