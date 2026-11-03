#include <cstdint>

std::uint32_t g_data = 0;

std::uint32_t* get_global_address() {
    return &g_data;
}

int main() {
    std::uint32_t* p = get_global_address();
    *p = 7;
    return 0;
}
