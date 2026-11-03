thread_local int g_counter = 0;

int main()
{
    int total = 0;
    for (g_counter = 0; g_counter < 5; ++g_counter) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-1]
    {
        total += g_counter;
    }
    return total;
}
