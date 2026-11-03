struct Device
{
    struct Controller
    {
        struct Status { unsigned char code; unsigned char flags; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
        int level;
    } controller;
    unsigned char id;
};

int main()
{
    Device d{};
    d.controller.level = 1;
    d.id = 2;
    return 0;
}
