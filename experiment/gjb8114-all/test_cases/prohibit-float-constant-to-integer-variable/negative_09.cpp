int main()
{
    int value = 0;
    int& ref = value;
    ref = 9.5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-1]
    return ref;
}
