int main()
{
    enum Edata { Enum1 = 0, Enum2, Enum3 };
    unsigned int data = 0;
    data = Enum1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
    return 0;
}
