#define LOOP while // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

int main()
{
    int i = 0;
    LOOP (i < 1)
    {
        i = 1;
    }
    return 0;
}
