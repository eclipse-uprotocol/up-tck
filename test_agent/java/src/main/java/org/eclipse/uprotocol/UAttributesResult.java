package org.eclipse.uprotocol;

import org.eclipse.uprotocol.v1.UAttributes;

public class UAttributesResult {
	private UAttributes attr;
	private String errorMessage;
	private boolean passed = true;
	
	public UAttributesResult(UAttributes attr) {
		this.attr = attr;
		passed = true;
	}
	
	public UAttributesResult(String errorMessage) {
		this.errorMessage = errorMessage;
		passed = false;
	}
	
	public boolean hasPassed() {
		return passed;
	}
	
	public String getError() {
		return errorMessage;
	}
	
	public UAttributes getAttributes() {
		return attr;
	}
	
}
