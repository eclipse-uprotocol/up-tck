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
struct TestUUri {
        std::string auth;
        uint32_t ue_id;
        uint32_t ue_version_major;
        uint32_t resource_id;

        operator uprotocol::v1::UUri() const
        {
                uprotocol::v1::UUri ret;
                ret.set_authority_name(auth);
                ret.set_ue_id(ue_id);
                ret.set_ue_version_major(ue_version_major);
                ret.set_resource_id(resource_id);
                return ret;
        }

        std::string to_string() const
        {
                return std::string("<< ") + uprotocol::v1::UUri(*this).ShortDebugString() + " >>";
        }

        TestUUri withReqIdZero()
        {
            TestUUri ret = *this;
            ret.resource_id = 0;
            return ret;
        }
};

void test_pub_sub(shared_ptr<SocketUTransport> transport)
{
    TestUUri src{"10.0.0.1", 0x10001, 1, 0x8000};
    auto action_exact = [&](const uprotocol::v1::UMessage& msg) { cout << "#### got sub from pub" << endl; };

    auto lhandle1 = transport->registerListener(src, action_exact);

    for (auto i = 0; i < 2; i++) {
        {
            uprotocol::v1::UAttributes attr;
            attr.set_type(uprotocol::v1::UMESSAGE_TYPE_PUBLISH);
            *attr.mutable_id() = make_uuid();
            *attr.mutable_source() = src;
            attr.set_payload_format(uprotocol::v1::UPAYLOAD_FORMAT_TEXT);
            attr.set_ttl(1000);

            uprotocol::v1::UMessage msg;
            *msg.mutable_attributes() = attr;
            msg.set_payload(make_payload(i));

            auto result = transport->send(msg);
            usleep(10000);
        }
    }
}

void test_rpc_req(shared_ptr<SocketUTransport> transport)
{
    TestUUri src{"10.0.0.1", 0x10001, 1, 0};
    auto action_exact = [&](const uprotocol::v1::UMessage& msg) { cout << "#### got rpc req" << endl; };

    TestUUri sink{"10.0.0.2", 0x10002, 2, 2};

    auto lhandle0 = transport->registerListener(src, action_exact, sink);
    auto lhandle1 = transport->registerListener(src, action_exact);

    for (auto i = 0; i < 2; i++) {
        {
            uprotocol::v1::UAttributes attr;
            attr.set_type(uprotocol::v1::UMESSAGE_TYPE_REQUEST);
            *attr.mutable_id() = make_uuid();
            *attr.mutable_source() = src.withReqIdZero();
            *attr.mutable_sink() = sink;
            attr.set_priority(uprotocol::v1::UPRIORITY_CS4);
            attr.set_payload_format(uprotocol::v1::UPAYLOAD_FORMAT_TEXT);
            attr.set_ttl(1000);

            uprotocol::v1::UMessage msg;
            *msg.mutable_attributes() = attr;
            msg.set_payload(make_payload(i));

            auto result = transport->send(msg);
            usleep(10000);
        }
    }
}

void test_rpc_resp(shared_ptr<SocketUTransport> transport)
{
    TestUUri src{"10.0.0.1", 0x10001, 1, 0};
    auto action_exact = [&](const uprotocol::v1::UMessage& msg) { cout << "#### got rpc resp" << endl; };

    TestUUri sink{"10.0.0.2", 0x10002, 2, 2};

    auto lhandle0 = transport->registerListener(sink, action_exact, src);
    // auto lhandle1 = transport->registerListener(src, action_exact);

    for (auto i = 0; i < 2; i++) {
        {
            uprotocol::v1::UAttributes attr;
            attr.set_type(uprotocol::v1::UMESSAGE_TYPE_RESPONSE);
            *attr.mutable_id() = make_uuid();
            *attr.mutable_source() = sink;
            *attr.mutable_sink() = src;
            attr.set_priority(uprotocol::v1::UPRIORITY_CS4);
            attr.set_payload_format(uprotocol::v1::UPAYLOAD_FORMAT_TEXT);
            *attr.mutable_reqid() = make_uuid();

            uprotocol::v1::UMessage msg;
            *msg.mutable_attributes() = attr;
            msg.set_payload(make_payload(i));

            auto result = transport->send(msg);
            usleep(10000);
        }
    }
}

void test_notification(shared_ptr<SocketUTransport> transport)
{
    TestUUri src{"10.0.0.1", 0x18001, 1, 1};
    auto action_exact = [&](const uprotocol::v1::UMessage& msg) { cout << "#### got notification" << endl; };

    TestUUri sink{"10.0.0.2", 0x10002, 2, 1};

    auto lhandle0 = transport->registerListener(sink, action_exact, src);
    cout << "after registerListener" << endl;
    // auto lhandle1 = transport->registerListener(src, action_exact);

    for (auto i = 0; i < 2; i++) {
        {
            uprotocol::v1::UAttributes attr;
            attr.set_type(uprotocol::v1::UMESSAGE_TYPE_NOTIFICATION);
            *attr.mutable_id() = make_uuid();
            *attr.mutable_source() = src;
            *attr.mutable_sink() = sink.withReqIdZero();
            // attr.set_priority(uprotocol::v1::UPRIORITY_CS4);
            attr.set_payload_format(uprotocol::v1::UPAYLOAD_FORMAT_TEXT);
            // *attr.mutable_reqid() = make_uuid();

            uprotocol::v1::UMessage msg;
            *msg.mutable_attributes() = attr;
            msg.set_payload(make_payload(i));

            auto result = transport->send(msg);
            usleep(10000);
        }
    }
}

int main(int argc, char *argv[])
{
    TestUUri def_src_uuri{"dev_src", 0x18000, 1, 0};
    auto transport = make_shared<SocketUTransport>(def_src_uuri);

    // test_pub_sub(transport);
    // test_rpc_req(transport);
    // test_rpc_resp(transport);
    test_notification(transport);
}
