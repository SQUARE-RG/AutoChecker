int main()
{
    int *ptr;
    bool is_null = (ptr == nullptr); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-1]
    return is_null ? 1 : 0;
}
