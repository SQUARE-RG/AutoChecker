#include <cstdio>
#include <memory>

int countLines(const char *path)
{
    std::unique_ptr<FILE, int (*)(FILE *)> stream(std::fopen(path, "r"), std::fclose);
    if (!stream) {
        std::printf("The file '%s' was not opened\n", path);
        return -1;
    }

    int lines = 0;
    char ch;
    while (std::fscanf(stream.get(), "%c", &ch) == 1) {
        if (ch == '\n') {
            ++lines;
        }
    }

    return lines;
}
