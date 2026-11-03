int fun1(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-13]

int main()
{
    return fun1();
}

int fun1()
{
    return 0;
}
