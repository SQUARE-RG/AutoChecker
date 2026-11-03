template <typename T>
struct Flags
{
    short count : 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
    signed short mode : 2;
    unsigned short reserved : 10;
    T payload;
};

int main()
{
    Flags<int> f{};
    f.count = 1;
    f.mode = 1;
    f.reserved = 0;
    f.payload = 0;
    return 0;
}
