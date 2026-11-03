#include <cstdio>
#include <cstddef>

namespace io
{
    int read_line(char *buffer, std::size_t size)
    {
        if (std::fgets(buffer, static_cast<int>(size), stdin) == nullptr)
        {
            return -1;
        }
        return 0;
    }
}

int main()
{
    char line[32] = {0};
    if (io::read_line(line, sizeof(line)) != 0)
    {
        std::printf("cannot read input\n");
        return 1;
    }
    std::printf("Read: %s\n", line);
    return 0;
}
