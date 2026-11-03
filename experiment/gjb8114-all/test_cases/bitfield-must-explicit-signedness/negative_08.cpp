union Bits
{
    short value : 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
    signed int whole : 8;
};

int main()
{
    Bits b{};
    b.value = 1;
    b.whole = 0;
    return 0;
}
