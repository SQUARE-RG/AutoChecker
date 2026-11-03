#include <cstdint>

struct DualPortCommandBlock {
    std::uint16_t command;
    std::uint16_t status;
};

// Mapped to dual-port memory; external hardware writes these fields asynchronously.
DualPortCommandBlock g_dual_port_block; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-12]

std::uint16_t read_status() {
    return g_dual_port_block.status;
}

void write_command(std::uint16_t command) {
    g_dual_port_block.command = command;
}
