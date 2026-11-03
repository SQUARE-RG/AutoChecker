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
    unsigned int raw = 7;
    Reading reading(raw);
    printf("%u\n", reading.get());
    return 0;
}
