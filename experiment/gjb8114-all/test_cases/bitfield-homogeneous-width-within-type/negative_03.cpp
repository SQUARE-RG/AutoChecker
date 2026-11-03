struct Data3
{
    int a : 31;
    int b : 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
};

int main()
{
    Data3 d{};
    return d.a + d.b;
}
