int fadd(int x, int y)
{
    return x + y;
}

int main()
{
    int x = 1;
    int y = 2;
    extern int fadd(int, int); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
    int result = fadd(x, y);
    return result;
}
