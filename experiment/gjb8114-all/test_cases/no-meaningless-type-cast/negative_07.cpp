int twice(int value)
{
    return value * 2;
}

int main()
{
    int x = 21;
    int y = twice((int)x); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
    return y - 42;
}
