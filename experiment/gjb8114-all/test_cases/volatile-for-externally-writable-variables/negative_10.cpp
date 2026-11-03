#include <cstdint>

std::uint32_t config_value = 0;

// 外部配置线程会异步改写该指针，使它指向新的配置槽。
std::uint32_t* external_config_ptr = &config_value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-12]

std::uint32_t read_external_config()
{
    return *external_config_ptr;
}
