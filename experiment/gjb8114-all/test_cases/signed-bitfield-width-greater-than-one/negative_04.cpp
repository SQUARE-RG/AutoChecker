union PackedValue {
    signed int small : 1;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
    unsigned int wide : 8;
};

int main(void)
{
    PackedValue value;
    value.small = -1;
    return 0;
}
