int zdata = 0;

int fadd(int x, int y)
{
    int z;
    z = x + y;
    return z;
}

int main()
{
    extern int zdata; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
    int x = 1;
    int y = 2;
    zdata = fadd(x, y);
    return 0;
}
