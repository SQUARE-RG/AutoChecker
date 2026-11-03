int fun(int datax, ...) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-15]
{
    return datax;
}

int main()
{
    return fun(1);
}
