typedef int Integer;

int scale(Integer n); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]

int scale(long n)
{
    return static_cast<int>(n * 2);
}

int main()
{
    return scale(1L);
}
