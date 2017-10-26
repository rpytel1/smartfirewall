/*
 * Copyright © 2017 Opendaylight and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */
package org.opendaylight.smartfirewall.cli.impl;

import org.opendaylight.controller.md.sal.binding.api.DataBroker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.opendaylight.smartfirewall.cli.api.SmartfirewallCliCommands;

public class SmartfirewallCliCommandsImpl implements SmartfirewallCliCommands {

    private static final Logger LOG = LoggerFactory.getLogger(SmartfirewallCliCommandsImpl.class);
    private final DataBroker dataBroker;

    public SmartfirewallCliCommandsImpl(final DataBroker db) {
        this.dataBroker = db;
        LOG.info("SmartfirewallCliCommandImpl initialized");
    }

    @Override
    public Object testCommand(Object testArgument) {
        return "This is a test implementation of test-command";
    }
}