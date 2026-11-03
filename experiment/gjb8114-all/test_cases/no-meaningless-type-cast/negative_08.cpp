int add(int a, int b)
{
    return static_cast<int>(a + b); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
}

int main()
{
    return add(4, 5) - 9;
}
