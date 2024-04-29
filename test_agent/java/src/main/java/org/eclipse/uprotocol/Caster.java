package org.eclipse.uprotocol;

public final class Caster {
	
	private Caster() {
	}
	
	public static int toInt(Object value) {
		int integer = 0;
    	if (value instanceof Double) {
    		double d = (double) value; 
    		integer = (int) d;
    	}
    	else if (value instanceof Float) {
    		float f = (float) value;
    		integer = (int) f;
    	}
    	else if (value instanceof Integer) {
    		integer = (int) value;
    	}
    	else {
    		integer = Integer.parseInt(value.toString());
    	}
    	return integer;
	}
	
	public static long toLong(Object value) {
		long longVal = 0;
    	if (value instanceof Double) {
    		double d = (double) value; 
    		longVal = (long) d;
    	}
    	else if (value instanceof Float) {
    		float f = (float) value;
    		longVal = (long) f;
    	}
    	else if (value instanceof Integer) {
    		longVal = (long) value;
    	}
    	else if (value instanceof Long) {
    		longVal = (long) value;
    	}
    	else {
    		try {
        		longVal = Long.parseLong(value.toString());
            } catch (NumberFormatException ex) {
        		longVal = Long.parseUnsignedLong(value.toString());
            }
    	}
    	return longVal;
	}
	
	public static float toFloat(Object value) {
		float f = 0;
		if (value instanceof Double) {
    		double d = (double) value; 
    		f = (float) d;
    	}
    	else if (value instanceof Float) {
    		f = (float) value;
    	}
    	else if (value instanceof Integer) {
    		int i = (int) value;
    		f = (float) i;
    	}
    	else {
    		f = Float.parseFloat(value.toString());
    	}
		return f;
	}
	
	public static double toDouble(Object value) {
		double d = 0;
		if (value instanceof Double) {
    		d = (double) value; 
    	}
    	else if (value instanceof Float) {
    		float f = (float) value;
    		d = (double) f; 
    	}
    	else if (value instanceof Integer) {
    		int i = (int) value;
    		d = (double) i;
    	}
    	else {
    		d = Double.parseDouble(value.toString());
    	}
		return d;
	}
	
}
