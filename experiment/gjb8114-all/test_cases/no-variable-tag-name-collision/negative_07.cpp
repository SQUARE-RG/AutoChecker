#include <cstdint>

struct Settings
{
    int volume;
};

int main()
{
    Settings config;
    Settings &Settings = config; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
    Settings.volume = 1;
    return 0;
}
