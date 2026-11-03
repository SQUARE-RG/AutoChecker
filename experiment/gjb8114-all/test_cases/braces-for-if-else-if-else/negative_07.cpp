int main()
{
    if constexpr (sizeof(int) == 4)
        return 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-2]
    else
    {
        return 1;
    }
}
