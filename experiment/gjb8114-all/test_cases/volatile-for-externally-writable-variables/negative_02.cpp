#include <cstdint>

// Memory-mapped status register of a peripheral device.
// The device writes it asynchronously, so its contents change outside program control.
std::uint32_t* const g_status_register = reinterpret_cast<std::uint32_t*>(0x40021000u); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-12]

std::uint32_t read_device_status() {
    return *g_status_register;
}

int main() {
    return 0;
}
