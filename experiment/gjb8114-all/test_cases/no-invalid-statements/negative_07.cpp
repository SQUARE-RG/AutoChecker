int negative_07(int a, int b)
{
    (a, b); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-3]
    return a + b;
}

int main()
{
    return negative_07(1, 2);
}
