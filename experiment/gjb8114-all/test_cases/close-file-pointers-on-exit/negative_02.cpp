#include <cstdio>

int countLines(const char *path)
{
    FILE *stream = std::fopen(path, "r");
    if (stream == nullptr) {
        std::printf("The file '%s' was not opened\n", path);
        return -1;
    }

    int lines = 0;
    char ch;
    while (std::fscanf(stream, "%c", &ch) == 1) {
        if (ch == '\n') {
            ++lines;
        }
        if (lines > 1000) {
            std::printf("too many lines\n");
            return -1; // CHECK-MESSAGES: :[[@LINE]]:13: warning: file pointer 'stream' is not closed before function exit [ucassaat-r-1-3-10]
        }
    }

    std::fclose(stream);
    return lines;
}
