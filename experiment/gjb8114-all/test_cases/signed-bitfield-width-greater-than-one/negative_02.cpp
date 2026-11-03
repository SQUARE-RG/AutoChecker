struct Mixed
{
    signed int low : 1, high : 3; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
    unsigned int data : 28;
};

int main()
{
    Mixed value{};
    value.low = 0;
    value.high = 0;
    return 0;
}
