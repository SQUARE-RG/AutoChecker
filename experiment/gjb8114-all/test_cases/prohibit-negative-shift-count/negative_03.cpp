int main()
{
    unsigned int xdata = 8;
    xdata = xdata << (1 - 3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return 0;
}
