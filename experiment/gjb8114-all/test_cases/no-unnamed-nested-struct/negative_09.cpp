struct Frame
{
    struct alignas(16) Chunk { int data; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
};

int main()
{
    Frame frame{};
    (void)frame;
    return 0;
}
