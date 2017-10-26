/*
 * Copyright (c) 2016 Ericsson India Global Services Pvt Ltd. and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */


package org.opendaylight.smartfirewall.impl;

import java.math.BigInteger;

public class FirewallConstants {

    /*
     * define sample flow constants
     */
    public static final String FLOWID_PREFIX = "sampleapp";
    public static final String FLOWID_SEPARATOR = ".";
    public static final String RULENAME_SEPARATOR = ":";
    public static final int ETH_TYPE = 34525 ;
    public static final BigInteger COOKIE_SAMPLEAPP_BASE = new BigInteger("1000000",
            16);
    public static final int FLOW_PRIORITY = 5;
    public static final int DEFAULT_TIMEOUT_VALUE = 0;
    public static final String SUBNET_MASK_SEPARATOR = "/";
    public static final String DEFAULT_RULE_NAME = "DEFAULT";

}
