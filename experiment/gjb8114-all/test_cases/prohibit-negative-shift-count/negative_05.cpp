enum ShiftCounts
{
    kNegativeLeftShift = -3
};

int main()
{
    int value = 8;
    value <<= kNegativeLeftShift; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return value;
}
