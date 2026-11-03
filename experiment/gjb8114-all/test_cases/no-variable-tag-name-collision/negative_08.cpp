#include <cstdint>

class Buffer
{
public:
    int data[2];
};

int main()
{
    Buffer Buffer[2]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
    Buffer[0].data[0] = 1;
    Buffer[1].data[1] = 2;
    return 0;
}
