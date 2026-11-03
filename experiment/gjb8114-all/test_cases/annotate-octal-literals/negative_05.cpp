int access_mode()
{
    return 0700; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-4]
}

int main()
{
    return access_mode();
}
