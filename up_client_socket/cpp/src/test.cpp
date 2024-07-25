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

    uprotocol::v1::UUri topic;
    topic.set_authority_name("topic");
    topic.set_ue_id(0x00010001);
    topic.set_ue_version_major(1);
    topic.set_resource_id(0x8000);
    auto action_exact = [&](const uprotocol::v1::UMessage& msg) { cout << "## action_exact" << endl; };

    uprotocol::v1::UUri topic_recv_all_topic;
    topic_recv_all_topic.set_authority_name("*");
    topic_recv_all_topic.set_ue_id(0x00010001);
    topic_recv_all_topic.set_ue_version_major(1);
    topic_recv_all_topic.set_resource_id(0x8000);
    auto action_all_topic = [&](const uprotocol::v1::UMessage& msg) { cout << "## action_all_topic" << endl; };


    uprotocol::v1::UUri topic_recv_all_ue_id;
    topic_recv_all_ue_id.set_authority_name("topic");
    topic_recv_all_ue_id.set_ue_id(0xffff);
    topic_recv_all_ue_id.set_ue_version_major(1);
    topic_recv_all_ue_id.set_resource_id(0x8000);
    auto action_all_ue_id = [&](const uprotocol::v1::UMessage& msg) { cout << "## action_all_ue_id" << endl; };

    uprotocol::v1::UUri topic_recv_all_vers_major;
    topic_recv_all_vers_major.set_authority_name("topic");
    topic_recv_all_vers_major.set_ue_id(0x00010001);
    topic_recv_all_vers_major.set_ue_version_major(0xffff);
    topic_recv_all_vers_major.set_resource_id(0x8000);
    auto action_all_vers_major = [&](const uprotocol::v1::UMessage& msg) { cout << "## action_all_vers_major" << endl; };

    uprotocol::v1::UUri topic_recv_all_resource_id;
    topic_recv_all_resource_id.set_authority_name("topic");
    topic_recv_all_resource_id.set_ue_id(0x00010001);
    topic_recv_all_resource_id.set_ue_version_major(1);
    topic_recv_all_resource_id.set_resource_id(0xffff);
    auto action_all_resource_id = [&](const uprotocol::v1::UMessage& msg) { cout << "## action_all_resource_id" << endl; };

    auto lhandle0 = transport->registerListener(topic, action_exact); ///, source_filter);
    // auto lhandle1 = transport->registerListener(topic_recv_all_topic, action_all_topic); ///, source_filter);
    // auto lhandle2 = transport->registerListener(topic_recv_all_ue_id, action_all_ue_id); ///, source_filter);
    auto lhandle3 = transport->registerListener(topic_recv_all_vers_major, action_all_vers_major); ///, source_filter);
    // auto lhandle4 = transport->registerListener(topic_recv_all_resource_id, action_all_resource_id); ///, source_filter);

    // auto lhandle2 = transport->registerListener(src1, action2); ///, source_filter);
    // auto lhandle3 = transport->registerListener(src2, action2); ///, source_filter);

    for (auto i = 0; i < 1; i++) {
        {
            uprotocol::v1::UAttributes attr;
            attr.set_type(uprotocol::v1::UMESSAGE_TYPE_PUBLISH);
            *attr.mutable_id() = make_uuid();
            *attr.mutable_source() = topic;
            // *attr.mutable_sink() = dest;
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
