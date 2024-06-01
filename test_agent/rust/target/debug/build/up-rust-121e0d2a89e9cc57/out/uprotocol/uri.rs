// This file is generated by rust-protobuf 3.4.0. Do not edit
// .proto file is parsed by protoc 3.19.4
// @generated

// https://github.com/rust-lang/rust-clippy/issues/702
#![allow(unknown_lints)]
#![allow(clippy::all)]

#![allow(unused_attributes)]
#![cfg_attr(rustfmt, rustfmt::skip)]

#![allow(box_pointers)]
#![allow(dead_code)]
#![allow(missing_docs)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(non_upper_case_globals)]
#![allow(trivial_casts)]
#![allow(unused_results)]
#![allow(unused_mut)]

//! Generated file from `uri.proto`

/// Generated files are compatible only with the same version
/// of protobuf runtime.
const _PROTOBUF_VERSION_CHECK: () = ::protobuf::VERSION_3_4_0;

// @@protoc_insertion_point(message:uprotocol.v1.UUri)
#[derive(PartialEq,Clone,Default,Debug)]
pub struct UUri {
    // message fields
    // @@protoc_insertion_point(field:uprotocol.v1.UUri.authority)
    pub authority: ::protobuf::MessageField<UAuthority>,
    // @@protoc_insertion_point(field:uprotocol.v1.UUri.entity)
    pub entity: ::protobuf::MessageField<UEntity>,
    // @@protoc_insertion_point(field:uprotocol.v1.UUri.resource)
    pub resource: ::protobuf::MessageField<UResource>,
    // special fields
    // @@protoc_insertion_point(special_field:uprotocol.v1.UUri.special_fields)
    pub special_fields: ::protobuf::SpecialFields,
}

impl<'a> ::std::default::Default for &'a UUri {
    fn default() -> &'a UUri {
        <UUri as ::protobuf::Message>::default_instance()
    }
}

impl UUri {
    pub fn new() -> UUri {
        ::std::default::Default::default()
    }

    fn generated_message_descriptor_data() -> ::protobuf::reflect::GeneratedMessageDescriptorData {
        let mut fields = ::std::vec::Vec::with_capacity(3);
        let mut oneofs = ::std::vec::Vec::with_capacity(0);
        fields.push(::protobuf::reflect::rt::v2::make_message_field_accessor::<_, UAuthority>(
            "authority",
            |m: &UUri| { &m.authority },
            |m: &mut UUri| { &mut m.authority },
        ));
        fields.push(::protobuf::reflect::rt::v2::make_message_field_accessor::<_, UEntity>(
            "entity",
            |m: &UUri| { &m.entity },
            |m: &mut UUri| { &mut m.entity },
        ));
        fields.push(::protobuf::reflect::rt::v2::make_message_field_accessor::<_, UResource>(
            "resource",
            |m: &UUri| { &m.resource },
            |m: &mut UUri| { &mut m.resource },
        ));
        ::protobuf::reflect::GeneratedMessageDescriptorData::new_2::<UUri>(
            "UUri",
            fields,
            oneofs,
        )
    }
}

impl ::protobuf::Message for UUri {
    const NAME: &'static str = "UUri";

    fn is_initialized(&self) -> bool {
        true
    }

    fn merge_from(&mut self, is: &mut ::protobuf::CodedInputStream<'_>) -> ::protobuf::Result<()> {
        while let Some(tag) = is.read_raw_tag_or_eof()? {
            match tag {
                10 => {
                    ::protobuf::rt::read_singular_message_into_field(is, &mut self.authority)?;
                },
                18 => {
                    ::protobuf::rt::read_singular_message_into_field(is, &mut self.entity)?;
                },
                26 => {
                    ::protobuf::rt::read_singular_message_into_field(is, &mut self.resource)?;
                },
                tag => {
                    ::protobuf::rt::read_unknown_or_skip_group(tag, is, self.special_fields.mut_unknown_fields())?;
                },
            };
        }
        ::std::result::Result::Ok(())
    }

    // Compute sizes of nested messages
    #[allow(unused_variables)]
    fn compute_size(&self) -> u64 {
        let mut my_size = 0;
        if let Some(v) = self.authority.as_ref() {
            let len = v.compute_size();
            my_size += 1 + ::protobuf::rt::compute_raw_varint64_size(len) + len;
        }
        if let Some(v) = self.entity.as_ref() {
            let len = v.compute_size();
            my_size += 1 + ::protobuf::rt::compute_raw_varint64_size(len) + len;
        }
        if let Some(v) = self.resource.as_ref() {
            let len = v.compute_size();
            my_size += 1 + ::protobuf::rt::compute_raw_varint64_size(len) + len;
        }
        my_size += ::protobuf::rt::unknown_fields_size(self.special_fields.unknown_fields());
        self.special_fields.cached_size().set(my_size as u32);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream<'_>) -> ::protobuf::Result<()> {
        if let Some(v) = self.authority.as_ref() {
            ::protobuf::rt::write_message_field_with_cached_size(1, v, os)?;
        }
        if let Some(v) = self.entity.as_ref() {
            ::protobuf::rt::write_message_field_with_cached_size(2, v, os)?;
        }
        if let Some(v) = self.resource.as_ref() {
            ::protobuf::rt::write_message_field_with_cached_size(3, v, os)?;
        }
        os.write_unknown_fields(self.special_fields.unknown_fields())?;
        ::std::result::Result::Ok(())
    }

    fn special_fields(&self) -> &::protobuf::SpecialFields {
        &self.special_fields
    }

    fn mut_special_fields(&mut self) -> &mut ::protobuf::SpecialFields {
        &mut self.special_fields
    }

    fn new() -> UUri {
        UUri::new()
    }

    fn clear(&mut self) {
        self.authority.clear();
        self.entity.clear();
        self.resource.clear();
        self.special_fields.clear();
    }

    fn default_instance() -> &'static UUri {
        static instance: UUri = UUri {
            authority: ::protobuf::MessageField::none(),
            entity: ::protobuf::MessageField::none(),
            resource: ::protobuf::MessageField::none(),
            special_fields: ::protobuf::SpecialFields::new(),
        };
        &instance
    }
}

impl ::protobuf::MessageFull for UUri {
    fn descriptor() -> ::protobuf::reflect::MessageDescriptor {
        static descriptor: ::protobuf::rt::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::rt::Lazy::new();
        descriptor.get(|| file_descriptor().message_by_package_relative_name("UUri").unwrap()).clone()
    }
}

impl ::std::fmt::Display for UUri {
    fn fmt(&self, f: &mut ::std::fmt::Formatter<'_>) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for UUri {
    type RuntimeType = ::protobuf::reflect::rt::RuntimeTypeMessage<Self>;
}

// @@protoc_insertion_point(message:uprotocol.v1.UAuthority)
#[derive(PartialEq,Clone,Default,Debug)]
pub struct UAuthority {
    // message fields
    // @@protoc_insertion_point(field:uprotocol.v1.UAuthority.name)
    pub name: ::std::option::Option<::std::string::String>,
    // message oneof groups
    pub number: ::std::option::Option<uauthority::Number>,
    // special fields
    // @@protoc_insertion_point(special_field:uprotocol.v1.UAuthority.special_fields)
    pub special_fields: ::protobuf::SpecialFields,
}

impl<'a> ::std::default::Default for &'a UAuthority {
    fn default() -> &'a UAuthority {
        <UAuthority as ::protobuf::Message>::default_instance()
    }
}

impl UAuthority {
    pub fn new() -> UAuthority {
        ::std::default::Default::default()
    }

    // bytes ip = 2;

    pub fn ip(&self) -> &[u8] {
        match self.number {
            ::std::option::Option::Some(uauthority::Number::Ip(ref v)) => v,
            _ => &[],
        }
    }

    pub fn clear_ip(&mut self) {
        self.number = ::std::option::Option::None;
    }

    pub fn has_ip(&self) -> bool {
        match self.number {
            ::std::option::Option::Some(uauthority::Number::Ip(..)) => true,
            _ => false,
        }
    }

    // Param is passed by value, moved
    pub fn set_ip(&mut self, v: ::std::vec::Vec<u8>) {
        self.number = ::std::option::Option::Some(uauthority::Number::Ip(v))
    }

    // Mutable pointer to the field.
    pub fn mut_ip(&mut self) -> &mut ::std::vec::Vec<u8> {
        if let ::std::option::Option::Some(uauthority::Number::Ip(_)) = self.number {
        } else {
            self.number = ::std::option::Option::Some(uauthority::Number::Ip(::std::vec::Vec::new()));
        }
        match self.number {
            ::std::option::Option::Some(uauthority::Number::Ip(ref mut v)) => v,
            _ => panic!(),
        }
    }

    // Take field
    pub fn take_ip(&mut self) -> ::std::vec::Vec<u8> {
        if self.has_ip() {
            match self.number.take() {
                ::std::option::Option::Some(uauthority::Number::Ip(v)) => v,
                _ => panic!(),
            }
        } else {
            ::std::vec::Vec::new()
        }
    }

    // bytes id = 3;

    pub fn id(&self) -> &[u8] {
        match self.number {
            ::std::option::Option::Some(uauthority::Number::Id(ref v)) => v,
            _ => &[],
        }
    }

    pub fn clear_id(&mut self) {
        self.number = ::std::option::Option::None;
    }

    pub fn has_id(&self) -> bool {
        match self.number {
            ::std::option::Option::Some(uauthority::Number::Id(..)) => true,
            _ => false,
        }
    }

    // Param is passed by value, moved
    pub fn set_id(&mut self, v: ::std::vec::Vec<u8>) {
        self.number = ::std::option::Option::Some(uauthority::Number::Id(v))
    }

    // Mutable pointer to the field.
    pub fn mut_id(&mut self) -> &mut ::std::vec::Vec<u8> {
        if let ::std::option::Option::Some(uauthority::Number::Id(_)) = self.number {
        } else {
            self.number = ::std::option::Option::Some(uauthority::Number::Id(::std::vec::Vec::new()));
        }
        match self.number {
            ::std::option::Option::Some(uauthority::Number::Id(ref mut v)) => v,
            _ => panic!(),
        }
    }

    // Take field
    pub fn take_id(&mut self) -> ::std::vec::Vec<u8> {
        if self.has_id() {
            match self.number.take() {
                ::std::option::Option::Some(uauthority::Number::Id(v)) => v,
                _ => panic!(),
            }
        } else {
            ::std::vec::Vec::new()
        }
    }

    fn generated_message_descriptor_data() -> ::protobuf::reflect::GeneratedMessageDescriptorData {
        let mut fields = ::std::vec::Vec::with_capacity(3);
        let mut oneofs = ::std::vec::Vec::with_capacity(1);
        fields.push(::protobuf::reflect::rt::v2::make_option_accessor::<_, _>(
            "name",
            |m: &UAuthority| { &m.name },
            |m: &mut UAuthority| { &mut m.name },
        ));
        fields.push(::protobuf::reflect::rt::v2::make_oneof_deref_has_get_set_simpler_accessor::<_, _>(
            "ip",
            UAuthority::has_ip,
            UAuthority::ip,
            UAuthority::set_ip,
        ));
        fields.push(::protobuf::reflect::rt::v2::make_oneof_deref_has_get_set_simpler_accessor::<_, _>(
            "id",
            UAuthority::has_id,
            UAuthority::id,
            UAuthority::set_id,
        ));
        oneofs.push(uauthority::Number::generated_oneof_descriptor_data());
        ::protobuf::reflect::GeneratedMessageDescriptorData::new_2::<UAuthority>(
            "UAuthority",
            fields,
            oneofs,
        )
    }
}

impl ::protobuf::Message for UAuthority {
    const NAME: &'static str = "UAuthority";

    fn is_initialized(&self) -> bool {
        true
    }

    fn merge_from(&mut self, is: &mut ::protobuf::CodedInputStream<'_>) -> ::protobuf::Result<()> {
        while let Some(tag) = is.read_raw_tag_or_eof()? {
            match tag {
                10 => {
                    self.name = ::std::option::Option::Some(is.read_string()?);
                },
                18 => {
                    self.number = ::std::option::Option::Some(uauthority::Number::Ip(is.read_bytes()?));
                },
                26 => {
                    self.number = ::std::option::Option::Some(uauthority::Number::Id(is.read_bytes()?));
                },
                tag => {
                    ::protobuf::rt::read_unknown_or_skip_group(tag, is, self.special_fields.mut_unknown_fields())?;
                },
            };
        }
        ::std::result::Result::Ok(())
    }

    // Compute sizes of nested messages
    #[allow(unused_variables)]
    fn compute_size(&self) -> u64 {
        let mut my_size = 0;
        if let Some(v) = self.name.as_ref() {
            my_size += ::protobuf::rt::string_size(1, &v);
        }
        if let ::std::option::Option::Some(ref v) = self.number {
            match v {
                &uauthority::Number::Ip(ref v) => {
                    my_size += ::protobuf::rt::bytes_size(2, &v);
                },
                &uauthority::Number::Id(ref v) => {
                    my_size += ::protobuf::rt::bytes_size(3, &v);
                },
            };
        }
        my_size += ::protobuf::rt::unknown_fields_size(self.special_fields.unknown_fields());
        self.special_fields.cached_size().set(my_size as u32);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream<'_>) -> ::protobuf::Result<()> {
        if let Some(v) = self.name.as_ref() {
            os.write_string(1, v)?;
        }
        if let ::std::option::Option::Some(ref v) = self.number {
            match v {
                &uauthority::Number::Ip(ref v) => {
                    os.write_bytes(2, v)?;
                },
                &uauthority::Number::Id(ref v) => {
                    os.write_bytes(3, v)?;
                },
            };
        }
        os.write_unknown_fields(self.special_fields.unknown_fields())?;
        ::std::result::Result::Ok(())
    }

    fn special_fields(&self) -> &::protobuf::SpecialFields {
        &self.special_fields
    }

    fn mut_special_fields(&mut self) -> &mut ::protobuf::SpecialFields {
        &mut self.special_fields
    }

    fn new() -> UAuthority {
        UAuthority::new()
    }

    fn clear(&mut self) {
        self.name = ::std::option::Option::None;
        self.number = ::std::option::Option::None;
        self.number = ::std::option::Option::None;
        self.special_fields.clear();
    }

    fn default_instance() -> &'static UAuthority {
        static instance: UAuthority = UAuthority {
            name: ::std::option::Option::None,
            number: ::std::option::Option::None,
            special_fields: ::protobuf::SpecialFields::new(),
        };
        &instance
    }
}

impl ::protobuf::MessageFull for UAuthority {
    fn descriptor() -> ::protobuf::reflect::MessageDescriptor {
        static descriptor: ::protobuf::rt::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::rt::Lazy::new();
        descriptor.get(|| file_descriptor().message_by_package_relative_name("UAuthority").unwrap()).clone()
    }
}

impl ::std::fmt::Display for UAuthority {
    fn fmt(&self, f: &mut ::std::fmt::Formatter<'_>) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for UAuthority {
    type RuntimeType = ::protobuf::reflect::rt::RuntimeTypeMessage<Self>;
}

/// Nested message and enums of message `UAuthority`
pub mod uauthority {

    #[derive(Clone,PartialEq,Debug)]
    #[non_exhaustive]
    // @@protoc_insertion_point(oneof:uprotocol.v1.UAuthority.number)
    pub enum Number {
        // @@protoc_insertion_point(oneof_field:uprotocol.v1.UAuthority.ip)
        Ip(::std::vec::Vec<u8>),
        // @@protoc_insertion_point(oneof_field:uprotocol.v1.UAuthority.id)
        Id(::std::vec::Vec<u8>),
    }

    impl ::protobuf::Oneof for Number {
    }

    impl ::protobuf::OneofFull for Number {
        fn descriptor() -> ::protobuf::reflect::OneofDescriptor {
            static descriptor: ::protobuf::rt::Lazy<::protobuf::reflect::OneofDescriptor> = ::protobuf::rt::Lazy::new();
            descriptor.get(|| <super::UAuthority as ::protobuf::MessageFull>::descriptor().oneof_by_name("number").unwrap()).clone()
        }
    }

    impl Number {
        pub(in super) fn generated_oneof_descriptor_data() -> ::protobuf::reflect::GeneratedOneofDescriptorData {
            ::protobuf::reflect::GeneratedOneofDescriptorData::new::<Number>("number")
        }
    }
}

// @@protoc_insertion_point(message:uprotocol.v1.UEntity)
#[derive(PartialEq,Clone,Default,Debug)]
pub struct UEntity {
    // message fields
    // @@protoc_insertion_point(field:uprotocol.v1.UEntity.name)
    pub name: ::std::string::String,
    // @@protoc_insertion_point(field:uprotocol.v1.UEntity.id)
    pub id: ::std::option::Option<u32>,
    // @@protoc_insertion_point(field:uprotocol.v1.UEntity.version_major)
    pub version_major: ::std::option::Option<u32>,
    // @@protoc_insertion_point(field:uprotocol.v1.UEntity.version_minor)
    pub version_minor: ::std::option::Option<u32>,
    // special fields
    // @@protoc_insertion_point(special_field:uprotocol.v1.UEntity.special_fields)
    pub special_fields: ::protobuf::SpecialFields,
}

impl<'a> ::std::default::Default for &'a UEntity {
    fn default() -> &'a UEntity {
        <UEntity as ::protobuf::Message>::default_instance()
    }
}

impl UEntity {
    pub fn new() -> UEntity {
        ::std::default::Default::default()
    }

    fn generated_message_descriptor_data() -> ::protobuf::reflect::GeneratedMessageDescriptorData {
        let mut fields = ::std::vec::Vec::with_capacity(4);
        let mut oneofs = ::std::vec::Vec::with_capacity(0);
        fields.push(::protobuf::reflect::rt::v2::make_simpler_field_accessor::<_, _>(
            "name",
            |m: &UEntity| { &m.name },
            |m: &mut UEntity| { &mut m.name },
        ));
        fields.push(::protobuf::reflect::rt::v2::make_option_accessor::<_, _>(
            "id",
            |m: &UEntity| { &m.id },
            |m: &mut UEntity| { &mut m.id },
        ));
        fields.push(::protobuf::reflect::rt::v2::make_option_accessor::<_, _>(
            "version_major",
            |m: &UEntity| { &m.version_major },
            |m: &mut UEntity| { &mut m.version_major },
        ));
        fields.push(::protobuf::reflect::rt::v2::make_option_accessor::<_, _>(
            "version_minor",
            |m: &UEntity| { &m.version_minor },
            |m: &mut UEntity| { &mut m.version_minor },
        ));
        ::protobuf::reflect::GeneratedMessageDescriptorData::new_2::<UEntity>(
            "UEntity",
            fields,
            oneofs,
        )
    }
}

impl ::protobuf::Message for UEntity {
    const NAME: &'static str = "UEntity";

    fn is_initialized(&self) -> bool {
        true
    }

    fn merge_from(&mut self, is: &mut ::protobuf::CodedInputStream<'_>) -> ::protobuf::Result<()> {
        while let Some(tag) = is.read_raw_tag_or_eof()? {
            match tag {
                10 => {
                    self.name = is.read_string()?;
                },
                16 => {
                    self.id = ::std::option::Option::Some(is.read_uint32()?);
                },
                24 => {
                    self.version_major = ::std::option::Option::Some(is.read_uint32()?);
                },
                32 => {
                    self.version_minor = ::std::option::Option::Some(is.read_uint32()?);
                },
                tag => {
                    ::protobuf::rt::read_unknown_or_skip_group(tag, is, self.special_fields.mut_unknown_fields())?;
                },
            };
        }
        ::std::result::Result::Ok(())
    }

    // Compute sizes of nested messages
    #[allow(unused_variables)]
    fn compute_size(&self) -> u64 {
        let mut my_size = 0;
        if !self.name.is_empty() {
            my_size += ::protobuf::rt::string_size(1, &self.name);
        }
        if let Some(v) = self.id {
            my_size += ::protobuf::rt::uint32_size(2, v);
        }
        if let Some(v) = self.version_major {
            my_size += ::protobuf::rt::uint32_size(3, v);
        }
        if let Some(v) = self.version_minor {
            my_size += ::protobuf::rt::uint32_size(4, v);
        }
        my_size += ::protobuf::rt::unknown_fields_size(self.special_fields.unknown_fields());
        self.special_fields.cached_size().set(my_size as u32);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream<'_>) -> ::protobuf::Result<()> {
        if !self.name.is_empty() {
            os.write_string(1, &self.name)?;
        }
        if let Some(v) = self.id {
            os.write_uint32(2, v)?;
        }
        if let Some(v) = self.version_major {
            os.write_uint32(3, v)?;
        }
        if let Some(v) = self.version_minor {
            os.write_uint32(4, v)?;
        }
        os.write_unknown_fields(self.special_fields.unknown_fields())?;
        ::std::result::Result::Ok(())
    }

    fn special_fields(&self) -> &::protobuf::SpecialFields {
        &self.special_fields
    }

    fn mut_special_fields(&mut self) -> &mut ::protobuf::SpecialFields {
        &mut self.special_fields
    }

    fn new() -> UEntity {
        UEntity::new()
    }

    fn clear(&mut self) {
        self.name.clear();
        self.id = ::std::option::Option::None;
        self.version_major = ::std::option::Option::None;
        self.version_minor = ::std::option::Option::None;
        self.special_fields.clear();
    }

    fn default_instance() -> &'static UEntity {
        static instance: UEntity = UEntity {
            name: ::std::string::String::new(),
            id: ::std::option::Option::None,
            version_major: ::std::option::Option::None,
            version_minor: ::std::option::Option::None,
            special_fields: ::protobuf::SpecialFields::new(),
        };
        &instance
    }
}

impl ::protobuf::MessageFull for UEntity {
    fn descriptor() -> ::protobuf::reflect::MessageDescriptor {
        static descriptor: ::protobuf::rt::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::rt::Lazy::new();
        descriptor.get(|| file_descriptor().message_by_package_relative_name("UEntity").unwrap()).clone()
    }
}

impl ::std::fmt::Display for UEntity {
    fn fmt(&self, f: &mut ::std::fmt::Formatter<'_>) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for UEntity {
    type RuntimeType = ::protobuf::reflect::rt::RuntimeTypeMessage<Self>;
}

// @@protoc_insertion_point(message:uprotocol.v1.UResource)
#[derive(PartialEq,Clone,Default,Debug)]
pub struct UResource {
    // message fields
    // @@protoc_insertion_point(field:uprotocol.v1.UResource.name)
    pub name: ::std::string::String,
    // @@protoc_insertion_point(field:uprotocol.v1.UResource.instance)
    pub instance: ::std::option::Option<::std::string::String>,
    // @@protoc_insertion_point(field:uprotocol.v1.UResource.message)
    pub message: ::std::option::Option<::std::string::String>,
    // @@protoc_insertion_point(field:uprotocol.v1.UResource.id)
    pub id: ::std::option::Option<u32>,
    // special fields
    // @@protoc_insertion_point(special_field:uprotocol.v1.UResource.special_fields)
    pub special_fields: ::protobuf::SpecialFields,
}

impl<'a> ::std::default::Default for &'a UResource {
    fn default() -> &'a UResource {
        <UResource as ::protobuf::Message>::default_instance()
    }
}

impl UResource {
    pub fn new() -> UResource {
        ::std::default::Default::default()
    }

    fn generated_message_descriptor_data() -> ::protobuf::reflect::GeneratedMessageDescriptorData {
        let mut fields = ::std::vec::Vec::with_capacity(4);
        let mut oneofs = ::std::vec::Vec::with_capacity(0);
        fields.push(::protobuf::reflect::rt::v2::make_simpler_field_accessor::<_, _>(
            "name",
            |m: &UResource| { &m.name },
            |m: &mut UResource| { &mut m.name },
        ));
        fields.push(::protobuf::reflect::rt::v2::make_option_accessor::<_, _>(
            "instance",
            |m: &UResource| { &m.instance },
            |m: &mut UResource| { &mut m.instance },
        ));
        fields.push(::protobuf::reflect::rt::v2::make_option_accessor::<_, _>(
            "message",
            |m: &UResource| { &m.message },
            |m: &mut UResource| { &mut m.message },
        ));
        fields.push(::protobuf::reflect::rt::v2::make_option_accessor::<_, _>(
            "id",
            |m: &UResource| { &m.id },
            |m: &mut UResource| { &mut m.id },
        ));
        ::protobuf::reflect::GeneratedMessageDescriptorData::new_2::<UResource>(
            "UResource",
            fields,
            oneofs,
        )
    }
}

impl ::protobuf::Message for UResource {
    const NAME: &'static str = "UResource";

    fn is_initialized(&self) -> bool {
        true
    }

    fn merge_from(&mut self, is: &mut ::protobuf::CodedInputStream<'_>) -> ::protobuf::Result<()> {
        while let Some(tag) = is.read_raw_tag_or_eof()? {
            match tag {
                10 => {
                    self.name = is.read_string()?;
                },
                18 => {
                    self.instance = ::std::option::Option::Some(is.read_string()?);
                },
                26 => {
                    self.message = ::std::option::Option::Some(is.read_string()?);
                },
                32 => {
                    self.id = ::std::option::Option::Some(is.read_uint32()?);
                },
                tag => {
                    ::protobuf::rt::read_unknown_or_skip_group(tag, is, self.special_fields.mut_unknown_fields())?;
                },
            };
        }
        ::std::result::Result::Ok(())
    }

    // Compute sizes of nested messages
    #[allow(unused_variables)]
    fn compute_size(&self) -> u64 {
        let mut my_size = 0;
        if !self.name.is_empty() {
            my_size += ::protobuf::rt::string_size(1, &self.name);
        }
        if let Some(v) = self.instance.as_ref() {
            my_size += ::protobuf::rt::string_size(2, &v);
        }
        if let Some(v) = self.message.as_ref() {
            my_size += ::protobuf::rt::string_size(3, &v);
        }
        if let Some(v) = self.id {
            my_size += ::protobuf::rt::uint32_size(4, v);
        }
        my_size += ::protobuf::rt::unknown_fields_size(self.special_fields.unknown_fields());
        self.special_fields.cached_size().set(my_size as u32);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream<'_>) -> ::protobuf::Result<()> {
        if !self.name.is_empty() {
            os.write_string(1, &self.name)?;
        }
        if let Some(v) = self.instance.as_ref() {
            os.write_string(2, v)?;
        }
        if let Some(v) = self.message.as_ref() {
            os.write_string(3, v)?;
        }
        if let Some(v) = self.id {
            os.write_uint32(4, v)?;
        }
        os.write_unknown_fields(self.special_fields.unknown_fields())?;
        ::std::result::Result::Ok(())
    }

    fn special_fields(&self) -> &::protobuf::SpecialFields {
        &self.special_fields
    }

    fn mut_special_fields(&mut self) -> &mut ::protobuf::SpecialFields {
        &mut self.special_fields
    }

    fn new() -> UResource {
        UResource::new()
    }

    fn clear(&mut self) {
        self.name.clear();
        self.instance = ::std::option::Option::None;
        self.message = ::std::option::Option::None;
        self.id = ::std::option::Option::None;
        self.special_fields.clear();
    }

    fn default_instance() -> &'static UResource {
        static instance: UResource = UResource {
            name: ::std::string::String::new(),
            instance: ::std::option::Option::None,
            message: ::std::option::Option::None,
            id: ::std::option::Option::None,
            special_fields: ::protobuf::SpecialFields::new(),
        };
        &instance
    }
}

impl ::protobuf::MessageFull for UResource {
    fn descriptor() -> ::protobuf::reflect::MessageDescriptor {
        static descriptor: ::protobuf::rt::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::rt::Lazy::new();
        descriptor.get(|| file_descriptor().message_by_package_relative_name("UResource").unwrap()).clone()
    }
}

impl ::std::fmt::Display for UResource {
    fn fmt(&self, f: &mut ::std::fmt::Formatter<'_>) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for UResource {
    type RuntimeType = ::protobuf::reflect::rt::RuntimeTypeMessage<Self>;
}

// @@protoc_insertion_point(message:uprotocol.v1.UUriBatch)
#[derive(PartialEq,Clone,Default,Debug)]
pub struct UUriBatch {
    // message fields
    // @@protoc_insertion_point(field:uprotocol.v1.UUriBatch.uris)
    pub uris: ::std::vec::Vec<UUri>,
    // special fields
    // @@protoc_insertion_point(special_field:uprotocol.v1.UUriBatch.special_fields)
    pub special_fields: ::protobuf::SpecialFields,
}

impl<'a> ::std::default::Default for &'a UUriBatch {
    fn default() -> &'a UUriBatch {
        <UUriBatch as ::protobuf::Message>::default_instance()
    }
}

impl UUriBatch {
    pub fn new() -> UUriBatch {
        ::std::default::Default::default()
    }

    fn generated_message_descriptor_data() -> ::protobuf::reflect::GeneratedMessageDescriptorData {
        let mut fields = ::std::vec::Vec::with_capacity(1);
        let mut oneofs = ::std::vec::Vec::with_capacity(0);
        fields.push(::protobuf::reflect::rt::v2::make_vec_simpler_accessor::<_, _>(
            "uris",
            |m: &UUriBatch| { &m.uris },
            |m: &mut UUriBatch| { &mut m.uris },
        ));
        ::protobuf::reflect::GeneratedMessageDescriptorData::new_2::<UUriBatch>(
            "UUriBatch",
            fields,
            oneofs,
        )
    }
}

impl ::protobuf::Message for UUriBatch {
    const NAME: &'static str = "UUriBatch";

    fn is_initialized(&self) -> bool {
        true
    }

    fn merge_from(&mut self, is: &mut ::protobuf::CodedInputStream<'_>) -> ::protobuf::Result<()> {
        while let Some(tag) = is.read_raw_tag_or_eof()? {
            match tag {
                10 => {
                    self.uris.push(is.read_message()?);
                },
                tag => {
                    ::protobuf::rt::read_unknown_or_skip_group(tag, is, self.special_fields.mut_unknown_fields())?;
                },
            };
        }
        ::std::result::Result::Ok(())
    }

    // Compute sizes of nested messages
    #[allow(unused_variables)]
    fn compute_size(&self) -> u64 {
        let mut my_size = 0;
        for value in &self.uris {
            let len = value.compute_size();
            my_size += 1 + ::protobuf::rt::compute_raw_varint64_size(len) + len;
        };
        my_size += ::protobuf::rt::unknown_fields_size(self.special_fields.unknown_fields());
        self.special_fields.cached_size().set(my_size as u32);
        my_size
    }

    fn write_to_with_cached_sizes(&self, os: &mut ::protobuf::CodedOutputStream<'_>) -> ::protobuf::Result<()> {
        for v in &self.uris {
            ::protobuf::rt::write_message_field_with_cached_size(1, v, os)?;
        };
        os.write_unknown_fields(self.special_fields.unknown_fields())?;
        ::std::result::Result::Ok(())
    }

    fn special_fields(&self) -> &::protobuf::SpecialFields {
        &self.special_fields
    }

    fn mut_special_fields(&mut self) -> &mut ::protobuf::SpecialFields {
        &mut self.special_fields
    }

    fn new() -> UUriBatch {
        UUriBatch::new()
    }

    fn clear(&mut self) {
        self.uris.clear();
        self.special_fields.clear();
    }

    fn default_instance() -> &'static UUriBatch {
        static instance: UUriBatch = UUriBatch {
            uris: ::std::vec::Vec::new(),
            special_fields: ::protobuf::SpecialFields::new(),
        };
        &instance
    }
}

impl ::protobuf::MessageFull for UUriBatch {
    fn descriptor() -> ::protobuf::reflect::MessageDescriptor {
        static descriptor: ::protobuf::rt::Lazy<::protobuf::reflect::MessageDescriptor> = ::protobuf::rt::Lazy::new();
        descriptor.get(|| file_descriptor().message_by_package_relative_name("UUriBatch").unwrap()).clone()
    }
}

impl ::std::fmt::Display for UUriBatch {
    fn fmt(&self, f: &mut ::std::fmt::Formatter<'_>) -> ::std::fmt::Result {
        ::protobuf::text_format::fmt(self, f)
    }
}

impl ::protobuf::reflect::ProtobufValue for UUriBatch {
    type RuntimeType = ::protobuf::reflect::rt::RuntimeTypeMessage<Self>;
}

static file_descriptor_proto_data: &'static [u8] = b"\
    \n\turi.proto\x12\x0cuprotocol.v1\"\xa2\x01\n\x04UUri\x126\n\tauthority\
    \x18\x01\x20\x01(\x0b2\x18.uprotocol.v1.UAuthorityR\tauthority\x12-\n\
    \x06entity\x18\x02\x20\x01(\x0b2\x15.uprotocol.v1.UEntityR\x06entity\x12\
    3\n\x08resource\x18\x03\x20\x01(\x0b2\x17.uprotocol.v1.UResourceR\x08res\
    ource\"\\\n\nUAuthority\x12\x17\n\x04name\x18\x01\x20\x01(\tH\x01R\x04na\
    me\x88\x01\x01\x12\x10\n\x02ip\x18\x02\x20\x01(\x0cH\0R\x02ip\x12\x10\n\
    \x02id\x18\x03\x20\x01(\x0cH\0R\x02idB\x08\n\x06numberB\x07\n\x05_name\"\
    \xb1\x01\n\x07UEntity\x12\x12\n\x04name\x18\x01\x20\x01(\tR\x04name\x12\
    \x13\n\x02id\x18\x02\x20\x01(\rH\0R\x02id\x88\x01\x01\x12(\n\rversion_ma\
    jor\x18\x03\x20\x01(\rH\x01R\x0cversionMajor\x88\x01\x01\x12(\n\rversion\
    _minor\x18\x04\x20\x01(\rH\x02R\x0cversionMinor\x88\x01\x01B\x05\n\x03_i\
    dB\x10\n\x0e_version_majorB\x10\n\x0e_version_minor\"\x94\x01\n\tUResour\
    ce\x12\x12\n\x04name\x18\x01\x20\x01(\tR\x04name\x12\x1f\n\x08instance\
    \x18\x02\x20\x01(\tH\0R\x08instance\x88\x01\x01\x12\x1d\n\x07message\x18\
    \x03\x20\x01(\tH\x01R\x07message\x88\x01\x01\x12\x13\n\x02id\x18\x04\x20\
    \x01(\rH\x02R\x02id\x88\x01\x01B\x0b\n\t_instanceB\n\n\x08_messageB\x05\
    \n\x03_id\"3\n\tUUriBatch\x12&\n\x04uris\x18\x01\x20\x03(\x0b2\x12.uprot\
    ocol.v1.UUriR\x04urisB'\n\x18org.eclipse.uprotocol.v1B\tUUriProtoP\x01b\
    \x06proto3\
";

/// `FileDescriptorProto` object which was a source for this generated file
fn file_descriptor_proto() -> &'static ::protobuf::descriptor::FileDescriptorProto {
    static file_descriptor_proto_lazy: ::protobuf::rt::Lazy<::protobuf::descriptor::FileDescriptorProto> = ::protobuf::rt::Lazy::new();
    file_descriptor_proto_lazy.get(|| {
        ::protobuf::Message::parse_from_bytes(file_descriptor_proto_data).unwrap()
    })
}

/// `FileDescriptor` object which allows dynamic access to files
pub fn file_descriptor() -> &'static ::protobuf::reflect::FileDescriptor {
    static generated_file_descriptor_lazy: ::protobuf::rt::Lazy<::protobuf::reflect::GeneratedFileDescriptor> = ::protobuf::rt::Lazy::new();
    static file_descriptor: ::protobuf::rt::Lazy<::protobuf::reflect::FileDescriptor> = ::protobuf::rt::Lazy::new();
    file_descriptor.get(|| {
        let generated_file_descriptor = generated_file_descriptor_lazy.get(|| {
            let mut deps = ::std::vec::Vec::with_capacity(0);
            let mut messages = ::std::vec::Vec::with_capacity(5);
            messages.push(UUri::generated_message_descriptor_data());
            messages.push(UAuthority::generated_message_descriptor_data());
            messages.push(UEntity::generated_message_descriptor_data());
            messages.push(UResource::generated_message_descriptor_data());
            messages.push(UUriBatch::generated_message_descriptor_data());
            let mut enums = ::std::vec::Vec::with_capacity(0);
            ::protobuf::reflect::GeneratedFileDescriptor::new_generated(
                file_descriptor_proto(),
                deps,
                messages,
                enums,
            )
        });
        ::protobuf::reflect::FileDescriptor::new_generated_2(generated_file_descriptor)
    })
}