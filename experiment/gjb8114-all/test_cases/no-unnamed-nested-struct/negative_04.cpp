template <typename T>
struct Buffer
{
    T value;
    struct Metadata
    {
        unsigned int size;
    }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
};

int main()
{
    Buffer<int> buffer{};
    buffer.value = 1;
    return 0;
}
