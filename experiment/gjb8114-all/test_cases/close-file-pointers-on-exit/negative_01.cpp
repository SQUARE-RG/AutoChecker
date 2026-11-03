#include <cstdio>

int loadConfig(char *buffer, int size)
{
    FILE *stream = std::fopen("config.txt", "r");
    if (stream == nullptr) {
        return -1;
    }

    int count = 0;
    char ch;
    while (count < size - 1 && std::fscanf(stream, "%c", &ch) == 1) {
        buffer[count++] = ch;
    }
    buffer[count] = '\0';
    return 0; // CHECK-MESSAGES: :[[@LINE]]:5: warning: file pointer 'stream' is not closed before function exit [ucassaat-r-1-3-10]
}
