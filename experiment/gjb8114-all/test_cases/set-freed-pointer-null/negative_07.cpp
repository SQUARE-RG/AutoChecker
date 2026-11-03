#include <cstdlib>

int main()
{
    long* data = static_cast<long*>(std::malloc(sizeof(long)));
    if (data == nullptr)
    {
        return 1;
    }

    *data = 42L;

    do
    {
        std::free(data); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-6]
    } while (false);

    return 0;
}
