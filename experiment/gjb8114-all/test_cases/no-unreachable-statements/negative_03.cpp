int negative_03(int value)
{
    if (value < 0) {
        throw value;
        value = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
    }
    return value;
}

int main()
{
    return negative_03(1);
}
