package org.eclipse.uprotocol;

import java.util.*;

public class Test {
    public static void main(String[] args) 
    { 
        UUID uuid = UUID.fromString("0190c6fe-db8b-70c2-a28f-c98eb4b0d91c");
        

        System.out.println("The least significant 64 bit: " + uuid.getLeastSignificantBits()); 
        System.out.println("The most significant 64 bit: " + uuid.getMostSignificantBits()); 
    }
}
