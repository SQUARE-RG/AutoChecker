#define EXIT_LOOP break // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

int main()
{
    int count = 0;
    while (true)
    {
        ++count;
        if (count >= 3)
        {
            EXIT_LOOP;
        }
    }
    return 0;
}
