#include <cstdio>

class Reading
{
public:
    explicit Reading(unsigned int value)
        : stored(value)
    {
    }

    unsigned int get() const
    {
        return stored;
    }

private:
    unsigned int stored;
};

int main()
{
    unsigned short raw = 7;
    Reading reading(raw);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-2]
    printf("%u\n", reading.get());
    return 0;
}
