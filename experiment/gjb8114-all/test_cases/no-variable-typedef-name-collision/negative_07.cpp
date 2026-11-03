typedef unsigned int TData;

int main()
{
    if (TData TData = 1u; TData > 0u) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
    {
        return static_cast<int>(TData);
    }
    return 0;
}
