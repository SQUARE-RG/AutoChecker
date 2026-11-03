int fun2(int, int); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-13]

int main()
{
    return fun2(10, 5);
}

int fun2(int a, int b)
{
    return a - b;
}
