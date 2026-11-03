int main()
{
    bool value = !true; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-10]
    return value ? 0 : 1;
}
