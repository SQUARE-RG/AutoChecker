int main()
{
    unsigned int value = 0;
    unsigned int* ptr = &value;
    *ptr = -3; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-15]
    return 0;
}
