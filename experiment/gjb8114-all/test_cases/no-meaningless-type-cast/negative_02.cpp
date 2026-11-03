int main()
{
    unsigned int sx = 4;
    unsigned int sy = 10;
    unsigned int sz = 0;
    sz = (unsigned int)((float)((sx + sy) * 2 / 3)) + 0.5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
    return 0;
}
