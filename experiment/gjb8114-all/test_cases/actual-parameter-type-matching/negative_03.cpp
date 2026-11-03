long multiply(long factor);

int main()
{
    int value = 5;
    return static_cast<int>(multiply(value)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-2]
}

long multiply(long factor)
{
    return factor * 2;
}
