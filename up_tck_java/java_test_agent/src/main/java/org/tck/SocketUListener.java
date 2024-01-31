package org.tck;

import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.v1.*;

public class SocketUListener implements UListener {

    @Override
    public void onReceive(UUri topic, UPayload payload, UAttributes attributes) {
        System.out.println("Listener onReceived");
        System.out.println("MATTHEW is awesome!!!");
        System.out.println(payload);
    }
}