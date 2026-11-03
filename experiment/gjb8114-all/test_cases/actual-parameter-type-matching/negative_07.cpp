struct Buffer
{
    long operator[](long index) const
    {
        return index;
    }
};

int main()
{
    Buffer buffer;
    int index = 1;
    long value = buffer[index]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-2]
    (void)value;
    return 0;
}
