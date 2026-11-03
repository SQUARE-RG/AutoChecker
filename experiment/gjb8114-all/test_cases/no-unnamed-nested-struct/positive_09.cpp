struct Frame
{
    struct alignas(16) Chunk { int data; } chunk;
};

int main()
{
    Frame frame{};
    frame.chunk.data = 42;
    return 0;
}
