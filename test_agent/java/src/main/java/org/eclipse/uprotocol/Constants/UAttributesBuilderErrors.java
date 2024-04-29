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
