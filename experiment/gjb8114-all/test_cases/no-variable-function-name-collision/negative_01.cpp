void misdis(void)
{
}

int main(void)
{
    int misdis; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-3]
    misdis = 0;
    return 0;
}
