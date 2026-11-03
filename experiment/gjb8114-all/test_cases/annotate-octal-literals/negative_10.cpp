int main(void)
{
    char buffer[010]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-4]
    (void)buffer;
    return 0;
}
