int main()
{
    unsigned int ydata = 16;
    int shift = 3;
    shift -= 5;
    ydata >>= shift; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return 0;
}
