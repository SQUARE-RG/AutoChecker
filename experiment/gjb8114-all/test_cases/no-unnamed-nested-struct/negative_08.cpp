struct Registry
{
    struct Key { static constexpr int bits = 8; int value; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
    int count;
};

int main()
{
    Registry registry;
    registry.count = Registry::Key::bits;
    return 0;
}
