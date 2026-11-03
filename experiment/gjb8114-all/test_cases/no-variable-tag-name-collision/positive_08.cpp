#include <cstdint>

class Buffer
{
public:
    int data[2];
};

int main()
{
    Buffer buffers[2];
    buffers[0].data[0] = 1;
    buffers[1].data[1] = 2;
    return 0;
}
