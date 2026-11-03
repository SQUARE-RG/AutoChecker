int main()
{
    int value = 4;
    return value == 4 ? 0 : 1;
}

static void unused_after_main() // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-13]
{
}
