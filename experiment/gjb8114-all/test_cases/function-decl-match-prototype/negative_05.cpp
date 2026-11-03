int scale(short value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

int scale(int value)
{
    return value * 2;
}

int main()
{
    int input = 21;
    return scale(input) == 42 ? 0 : 1;
}
