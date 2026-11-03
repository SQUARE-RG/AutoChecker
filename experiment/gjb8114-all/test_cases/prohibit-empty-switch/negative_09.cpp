int main()
{
    signed char value = 0;
    try
    {
        switch (value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-3]
        }
    }
    catch (...)
    {
        return 1;
    }
    return 0;
}
