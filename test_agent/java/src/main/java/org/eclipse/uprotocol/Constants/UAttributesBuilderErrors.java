/*
 * Copyright (c) 2024 General Motors GTO LLC
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 * SPDX-FileType: SOURCE
 * SPDX-FileCopyrightText: 2024 General Motors GTO LLC
 * SPDX-License-Identifier: Apache-2.0
 */

package org.eclipse.uprotocol.Constants;

public class UAttributesBuilderErrors {
    
    public static String notGiven(String fieldName) {
    	return String.format("ERROR: \"%s\" field must exist", fieldName);
    }
    
    public static String badDataValue(String fieldName) {
    	if (fieldName.equals("priority")) {
    		return String.format("ERROR: \"%s\" field must be int between [0, 7]", fieldName);
    	}
    	else if (fieldName.equals("commstatus")) {
    		return String.format("ERROR: \"%s\" field must be int between [0, 16]", fieldName);
    	}
    	else {
    		return String.format("ERROR: same data type but bad value in \"%s\" uAttribute field assignment", fieldName);
    	}
    }
    
    public static String badDataType(String fieldName) {
    	return String.format("ERROR: data type misalignment in \"%s\" uAttribute field assignment", fieldName);
    }

}