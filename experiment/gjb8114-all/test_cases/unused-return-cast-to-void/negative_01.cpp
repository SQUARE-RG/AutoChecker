int compute_sign(int value)
{
    if (value >= 0)
    {
        return 1;
    }
    return -1;
}

int main()
{
    int local = -5;
    compute_sign(local); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-11]
    return 0;
}
