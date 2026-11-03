union // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-8]
{
    unsigned char cd[4];
    int id;
} uData;

int main()
{
    uData.id = 42;
    return uData.id;
}
