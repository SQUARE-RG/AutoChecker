int main()
{
    unsigned int stdin = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-4]
    return static_cast<int>(stdin);
}
