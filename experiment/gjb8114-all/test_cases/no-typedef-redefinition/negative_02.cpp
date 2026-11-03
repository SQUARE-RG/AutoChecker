int main()
{
    typedef int local_type;

    {
        typedef float local_type; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
        local_type x = 1.0f;
        (void)x;
    }

    return 0;
}
