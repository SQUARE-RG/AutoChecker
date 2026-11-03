namespace std
{
    void* malloc(unsigned long size) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-1]
    {
        (void)size;
        return nullptr;
    }
}

int main()
{
    void* p = std::malloc(10);
    (void)p;
    return 0;
}
