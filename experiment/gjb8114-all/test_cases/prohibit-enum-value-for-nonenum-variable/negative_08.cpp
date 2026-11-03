enum DeviceMode
{
    ModeIdle = 0,
    ModeActive = 1
};

struct DeviceConfig
{
    unsigned int mode;
};

int main()
{
    DeviceConfig config{};
    config.mode = ModeActive; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
    return 0;
}
