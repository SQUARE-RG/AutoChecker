extern volatile int g_count = 7; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-19]

int main()
{
    g_count = 8;
    return 0;
}
