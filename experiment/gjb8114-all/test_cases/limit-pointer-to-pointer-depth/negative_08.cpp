int main()
{
    int** pp = nullptr;
    void* raw = &pp;
    auto ppp = static_cast<int***>(raw); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-1]
    (void)ppp;
    return 0;
}
