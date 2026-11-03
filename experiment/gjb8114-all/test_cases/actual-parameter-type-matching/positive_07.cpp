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
    long index = 1;
    long value = buffer[index];
    (void)value;
    return 0;
}
