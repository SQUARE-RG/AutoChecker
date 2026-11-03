#include <cstdio>
#include <cstddef>

static int read_first_line(const char *path, char *out, std::size_t size)
{
    std::FILE *stream = std::fopen(path, "r");
    if (stream == nullptr) {
        return -1;
    }
    if (std::fgets(out, static_cast<int>(size), stream) == nullptr) {
        std::fclose(stream);
        return -2;
    }
    std::fclose(stream);
    return 0;
}

int main()
{
    char buffer[64];
    (void)read_first_line("data.txt", buffer, sizeof buffer);
    return 0;
}
