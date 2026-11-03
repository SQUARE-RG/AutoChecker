int adjust(int value)
{
    if (value > 0)
    {
        return value + 1;
    }
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]

int main()
{
    return adjust(1);
}
