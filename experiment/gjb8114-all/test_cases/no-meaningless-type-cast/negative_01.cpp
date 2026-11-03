int main()
{
    unsigned int sy = 10;
    unsigned int sx = (unsigned int)sy + 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
    return 0;
}
