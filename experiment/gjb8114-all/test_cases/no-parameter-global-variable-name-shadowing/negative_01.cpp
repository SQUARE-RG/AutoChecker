int sign = 0;

int func(int sign) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
{
    int local = sign;
    return local;
}

int main()
{
    return func(7);
}
