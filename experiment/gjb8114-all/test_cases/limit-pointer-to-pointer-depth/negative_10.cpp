int main()
{
    void* raw = nullptr;
    void* result = (int***)raw; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-1]
    return 0;
}
