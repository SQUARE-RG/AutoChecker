int main()
{
    unsigned short usX;
    usX = -10; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-15]
    return 0;
}
