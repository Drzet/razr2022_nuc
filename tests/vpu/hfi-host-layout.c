/* SPDX-License-Identifier: MIT
 * Synthetic HOST LP64 ABI smoke test. NOT a Qualcomm target build.
 * Type/field ordering copied from pinned Waipio hfi_command.h and upstream
 * Iris iris_hfi_gen2_packet.h, whose Git blob IDs are in audit-vpu-hfi.py.
 */
#include <stddef.h>
#include <stdint.h>

struct vendor_hfi_header {
    uint32_t size, session_id, header_id, reserved[4], num_packets;
};
struct mainline_iris_hfi_header {
    uint32_t size, session_id, header_id, reserved[4], num_packets;
};
struct vendor_hfi_packet {
    uint32_t size, type, flags, payload_info, port, packet_id, reserved[2];
};
struct mainline_iris_hfi_packet {
    uint32_t size, type, flags, payload_info, port, packet_id, reserved[2];
    uint32_t payload[];
};
struct vendor_hfi_buffer {
    uint32_t type, index;
    uint64_t base_address;
    uint32_t addr_offset, buffer_size, data_offset, data_size;
    uint64_t timestamp;
    uint32_t flags, reserved[5];
};
struct mainline_iris_hfi_buffer {
    uint32_t type, index;
    uint64_t base_address;
    uint32_t addr_offset, buffer_size, data_offset, data_size;
    uint64_t timestamp;
    uint32_t flags, reserved[5];
};

#define SAME(T, FIELD) \
    _Static_assert(offsetof(struct vendor_##T, FIELD) == \
                   offsetof(struct mainline_iris_##T, FIELD), #T "." #FIELD)
#define SIZE_EQ(T, SIZE) \
    _Static_assert(sizeof(struct vendor_##T) == (SIZE), #T " vendor size"); \
    _Static_assert(sizeof(struct mainline_iris_##T) == (SIZE), #T " upstream size")
SIZE_EQ(hfi_header, 32);
SIZE_EQ(hfi_packet, 32);
SIZE_EQ(hfi_buffer, 64);
SAME(hfi_header, size);
SAME(hfi_header, session_id);
SAME(hfi_header, header_id);
SAME(hfi_header, reserved);
SAME(hfi_header, num_packets);
SAME(hfi_packet, size);
SAME(hfi_packet, type);
SAME(hfi_packet, flags);
SAME(hfi_packet, payload_info);
SAME(hfi_packet, port);
SAME(hfi_packet, packet_id);
SAME(hfi_packet, reserved);
SAME(hfi_buffer, type);
SAME(hfi_buffer, index);
SAME(hfi_buffer, base_address);
SAME(hfi_buffer, addr_offset);
SAME(hfi_buffer, buffer_size);
SAME(hfi_buffer, data_offset);
SAME(hfi_buffer, data_size);
SAME(hfi_buffer, timestamp);
SAME(hfi_buffer, flags);
SAME(hfi_buffer, reserved);
_Static_assert(_Alignof(struct vendor_hfi_header) == 4, "header alignment");
_Static_assert(_Alignof(struct vendor_hfi_packet) == 4, "packet alignment");
_Static_assert(_Alignof(struct vendor_hfi_buffer) == 8, "buffer alignment");
_Static_assert(offsetof(struct mainline_iris_hfi_packet, payload) == 32,
               "upstream flexible payload offset");
int main(void) { return 0; }
