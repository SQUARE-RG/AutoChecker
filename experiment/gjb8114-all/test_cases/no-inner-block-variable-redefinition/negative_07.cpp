int main()
{
    int total = 0;

    try
    {
        int total = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
        total += 2;
    }
    catch (...)
    {
    }

    return total;
}
