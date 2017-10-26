/*
 * Copyright (c) 2016 Ericsson India Global Services Pvt Ltd. and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */

package org.opendaylight.smartfirewall.impl;

import org.opendaylight.yang.gen.v1.urn.opendaylight.flow.inventory.rev130819.FlowCapableNode;
import org.opendaylight.yang.gen.v1.urn.opendaylight.flow.inventory.rev130819.tables.Table;
import org.opendaylight.yang.gen.v1.urn.opendaylight.flow.inventory.rev130819.tables.TableKey;
import org.opendaylight.yang.gen.v1.urn.opendaylight.flow.inventory.rev130819.tables.table.Flow;
import org.opendaylight.yang.gen.v1.urn.opendaylight.flow.inventory.rev130819.tables.table.FlowBuilder;
import org.opendaylight.yang.gen.v1.urn.opendaylight.inventory.rev130819.NodeId;
import org.opendaylight.yang.gen.v1.urn.opendaylight.inventory.rev130819.Nodes;
import org.opendaylight.yang.gen.v1.urn.opendaylight.inventory.rev130819.nodes.Node;
import org.opendaylight.yang.gen.v1.urn.opendaylight.inventory.rev130819.nodes.NodeBuilder;
import org.opendaylight.yang.gen.v1.urn.opendaylight.inventory.rev130819.nodes.NodeKey;
import org.opendaylight.yangtools.yang.binding.InstanceIdentifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

//import org.opendaylight.yang.gen.v1.urn.opendaylight.flow.types.rev131026.flow.MatchBuilder;
//import org.opendaylight.yang.gen.v1.urn.opendaylight.flow.inventory.rev130819.tables.table.FlowKey;


public class SampleAppUtils {

    private static final Logger LOG = LoggerFactory.getLogger(FirewallDataStoreHandler.class);

    public static NodeBuilder getNodeBuilder(final String nodeId) {
        NodeBuilder nodeBuilder = new NodeBuilder();
        nodeBuilder.setId(new NodeId(nodeId));
        nodeBuilder.setKey(new NodeKey(nodeBuilder.getId()));
        return nodeBuilder;
    }

    public static final InstanceIdentifier<Flow> createFlowIdentifier(
            FlowBuilder flowBuilder, NodeBuilder nodeBuilder) {
        InstanceIdentifier<Flow> flowIdentifier = InstanceIdentifier
                .builder(Nodes.class).child(Node.class, nodeBuilder.getKey())
                .augmentation(FlowCapableNode.class)
                .child(Table.class, new TableKey(flowBuilder.getTableId()))
                .child(Flow.class, flowBuilder.getKey()).build();
        return flowIdentifier;
    }

    public static final InstanceIdentifier<Node> createNodeIdentifier(
            NodeBuilder nodeBuilder) {
        InstanceIdentifier<Node> nodeIdentifier = InstanceIdentifier
                .builder(Nodes.class).child(Node.class, nodeBuilder.getKey())
                .toInstance();
        return nodeIdentifier;
    }

    public static final InstanceIdentifier<Table> createTableIdentifier(FlowBuilder flowBuilder,
                                                                        NodeBuilder nodeBuilder) {
        InstanceIdentifier<Table> tableInstanceId = InstanceIdentifier
                .builder(Nodes.class).child(Node.class, nodeBuilder.getKey())
                .augmentation(FlowCapableNode.class)
                .child(Table.class, new TableKey(flowBuilder.getTableId())).build();
        return tableInstanceId;
    }

}
