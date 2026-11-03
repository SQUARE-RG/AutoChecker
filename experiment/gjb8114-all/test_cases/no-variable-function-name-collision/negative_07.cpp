void misdis(void)
{
}

int main(void)
{
    {
        int misdis = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-3]
        return misdis;
    }
}
