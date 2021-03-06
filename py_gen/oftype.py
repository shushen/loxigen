# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.

from collections import namedtuple

import loxi_utils.loxi_utils as loxi_utils
import py_gen.codegen
import loxi_globals

OFTypeData = namedtuple("OFTypeData", ["init", "pack", "unpack"])

# Map from LOXI type name to an object with templates for init, pack, and unpack
# Most types are defined using the convenience code below. This dict should
# only be used directly for special cases such as primitive types.
type_data_map = {
    'char': OFTypeData(
        init='0',
        pack='struct.pack("!B", %s)',
        unpack='%s.read("!B")[0]'),

    'uint8_t': OFTypeData(
        init='0',
        pack='struct.pack("!B", %s)',
        unpack='%s.read("!B")[0]'),

    'uint16_t': OFTypeData(
        init='0',
        pack='struct.pack("!H", %s)',
        unpack='%s.read("!H")[0]'),

    'uint32_t': OFTypeData(
        init='0',
        pack='struct.pack("!L", %s)',
        unpack='%s.read("!L")[0]'),

    'uint64_t': OFTypeData(
        init='0',
        pack='struct.pack("!Q", %s)',
        unpack='%s.read("!Q")[0]'),

    'of_port_no_t': OFTypeData(
        init='0',
        pack='util.pack_port_no(%s)',
        unpack='util.unpack_port_no(%s)'),

    'of_fm_cmd_t': OFTypeData(
        init='0',
        pack='util.pack_fm_cmd(%s)',
        unpack='util.unpack_fm_cmd(%s)'),

    'of_wc_bmap_t': OFTypeData(
        init='util.init_wc_bmap()',
        pack='util.pack_wc_bmap(%s)',
        unpack='util.unpack_wc_bmap(%s)'),

    'of_match_bmap_t': OFTypeData(
        init='util.init_match_bmap()',
        pack='util.pack_match_bmap(%s)',
        unpack='util.unpack_match_bmap(%s)'),

    'of_ipv4_t': OFTypeData(
        init='0',
        pack='struct.pack("!L", %s)',
        unpack='%s.read("!L")[0]'),

    'of_ipv6_t': OFTypeData(
        init="'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'",
        pack='struct.pack("!16s", %s)',
        unpack="%s.read('!16s')[0]"),

    'of_mac_addr_t': OFTypeData(
        init='[0,0,0,0,0,0]',
        pack='struct.pack("!6B", *%s)',
        unpack="list(%s.read('!6B'))"),

    'of_octets_t': OFTypeData(
        init="''",
        pack='%s',
        unpack='str(%s.read_all())'),

    'of_bitmap_128_t': OFTypeData(
        init='set()',
        pack='util.pack_bitmap_128(%s)',
        unpack="util.unpack_bitmap_128(%s)"),

    'of_oxm_t': OFTypeData(
        init='None',
        pack='%s.pack()',
        unpack='oxm.oxm.unpack(%s)'),

    'of_checksum_128_t': OFTypeData(
        init='0',
        pack='util.pack_checksum_128(%s)',
        unpack="util.unpack_checksum_128(%s)"),
}

## Fixed length strings

# Map from class name to length
fixed_length_strings = {
    'of_port_name_t': 16,
    'of_table_name_t': 32,
    'of_serial_num_t': 32,
    'of_desc_str_t': 256,
    'of_str64_t': 64,
}

for (cls, length) in fixed_length_strings.items():
    type_data_map[cls] = OFTypeData(
        init='""',
        pack='struct.pack("!%ds", %%s)' % length,
        unpack='%%s.read("!%ds")[0].rstrip("\\x00")' % length)

## Embedded structs

# Map from class name to Python class name
embedded_structs = {
    'of_match_t': 'common.match',
    'of_port_desc_t': 'common.port_desc',
    'of_meter_features_t': 'common.meter_features',
    'of_bsn_vport_t': 'common.bsn_vport',
}

for (cls, pyclass) in embedded_structs.items():
    type_data_map[cls] = OFTypeData(
        init='%s()' % pyclass,
        pack='%s.pack()',
        unpack='%s.unpack(%%s)' % pyclass)

## Public interface

def lookup_type_data(oftype, version):
    return type_data_map.get(loxi_utils.lookup_ir_wiretype(oftype, version))

# Return an initializer expression for the given oftype
def gen_init_expr(oftype, version):
    type_data = lookup_type_data(oftype, version)
    if type_data and type_data.init:
        return type_data.init
    elif oftype_is_list(oftype):
        return "[]"
    else:
        return "loxi.unimplemented('init %s')" % oftype

# Return a pack expression for the given oftype
#
# 'value_expr' is a string of Python code which will evaluate to
# the value to be packed.
def gen_pack_expr(oftype, value_expr, version):
    type_data = lookup_type_data(oftype, version)
    if type_data and type_data.pack:
        return type_data.pack % value_expr
    elif oftype_is_list(oftype):
        return "loxi.generic_util.pack_list(%s)" % value_expr
    else:
        return "loxi.unimplemented('pack %s')" % oftype

# Return an unpack expression for the given oftype
#
# 'reader_expr' is a string of Python code which will evaluate to
# the OFReader instance used for deserialization.
def gen_unpack_expr(oftype, reader_expr, version):
    type_data = lookup_type_data(oftype, version)
    if type_data and type_data.unpack:
        return type_data.unpack % reader_expr
    elif oftype_is_list(oftype):
        ofproto = loxi_globals.ir[version]
        ofclass = ofproto.class_by_name(oftype_list_elem(oftype))
        module_name, class_name = py_gen.codegen.generate_pyname(ofclass)
        return 'loxi.generic_util.unpack_list(%s, %s.%s.unpack)' % \
            (reader_expr, module_name, class_name)
    else:
        return "loxi.unimplemented('unpack %s')" % oftype

def oftype_is_list(oftype):
    return (oftype.find("list(") == 0)

# Converts "list(of_flow_stats_entry_t)" to "of_flow_stats_entry"
def oftype_list_elem(oftype):
    assert oftype.find("list(") == 0
    return oftype[5:-3]
