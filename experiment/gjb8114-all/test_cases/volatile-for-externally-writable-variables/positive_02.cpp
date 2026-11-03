#include <cstdint>

// Correctly declared: the pointer itself is const, but the pointed-to register
// is volatile because the peripheral device may change it at any time.
volatile std::uint32_t* const g_status_register =
    reinterpret_cast<volatile std::uint32_t*>(0x40021000u);

std::uint32_t read_device_status() {
    return *g_status_register;
}

int main() {
    return 0;
}
