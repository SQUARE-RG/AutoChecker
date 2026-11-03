typedef unsigned int TData;

int main()
{
    unsigned int values[3] = {1u, 2u, 3u};
    unsigned int sum = 0u;
    for (TData TData : values) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
    {
        sum += TData;
    }
    return static_cast<int>(sum);
}
