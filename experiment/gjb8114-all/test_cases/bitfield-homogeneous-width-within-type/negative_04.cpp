struct Data4
{
    unsigned char a : 5;
    unsigned char b : 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
};

int main()
{
    Data4 d{};
    return d.a + d.b;
}
