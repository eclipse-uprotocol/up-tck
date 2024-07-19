#include <iostream>
#include <sstream>
#include <unistd.h>
#include "SocketUTransport.h"
#include <up-cpp/datamodel/builder/Uuid.h>

using namespace std;

uprotocol::v1::UUID make_uuid() {
    auto id = uprotocol::datamodel::builder::UuidBuilder::getBuilder().build();
    return id;
}

string make_payload(int i)
{
    stringstream ss;
    ss << "payload_" << i;
    return ss.str();
}

int main(int argc, char *argv[])
{
    uprotocol::v1::UUri def_src_uuri;
    def_src_uuri.set_authority_name("def_src");
    def_src_uuri.set_ue_id(0x18000);
    def_src_uuri.set_ue_version_major(1);
    def_src_uuri.set_resource_id(0);

    auto transport = make_shared<SocketUTransport>(def_src_uuri);

    uprotocol::v1::UUri src1;
    src1.set_authority_name("src1");
    src1.set_ue_id(0x00010001);
    src1.set_ue_version_major(1);
    src1.set_resource_id(0x8000);

    uprotocol::v1::UUri src2;
    src2.set_authority_name("src2");
    src2.set_ue_id(0x00010001);
    src2.set_ue_version_major(1);
    src2.set_resource_id(0x8000);

    auto action1 = [&](const uprotocol::v1::UMessage& msg) {
        cout << "############################ action1" << endl;
        cout << msg.DebugString() << endl;
    };

    auto action2 = [&](const uprotocol::v1::UMessage& msg) {
        cout << "############################ action2" << endl;
        cout << msg.DebugString() << endl;
    };

    auto lhandle = transport->registerListener(src1, action1); ///, source_filter);
    auto lhandle2 = transport->registerListener(src1, action2); ///, source_filter);
    auto lhandle3 = transport->registerListener(src2, action2); ///, source_filter);

    for (auto i = 0; i < 2; i++) {
        {
            uprotocol::v1::UAttributes attr;
            attr.set_type(uprotocol::v1::UMESSAGE_TYPE_PUBLISH);
            *attr.mutable_id() = make_uuid();
            *attr.mutable_source() = src1;
            attr.set_payload_format(uprotocol::v1::UPAYLOAD_FORMAT_TEXT);
            attr.set_ttl(1000);

            uprotocol::v1::UMessage msg;
            *msg.mutable_attributes() = attr;
            msg.set_payload(make_payload(i));

            auto result = transport->send(msg);
            usleep(10000);
        }

        // {
        //     uprotocol::v1::UAttributes attr;
        //     attr.set_type(uprotocol::v1::UMESSAGE_TYPE_PUBLISH);
        //     *attr.mutable_id() = make_uuid();
        //     *attr.mutable_source() = src2;
        //     attr.set_payload_format(uprotocol::v1::UPAYLOAD_FORMAT_TEXT);
        //     attr.set_ttl(1000);

        //     uprotocol::v1::UMessage msg;
        //     *msg.mutable_attributes() = attr;
        //     msg.set_payload(make_payload(i*2));

        //     auto result = transport->send(msg);
        //     usleep(10000);
        // }
        sleep(1);
    }
    // sleep(10);
}
