#include <cstdio>

int read_with_goto(const char* path) {
    FILE* fp = std::fopen(path, "r");
    if (fp == nullptr) {
        return -1;
    }
    int value = 0;
    if (std::fscanf(fp, "%d", &value) != 1) {
        goto fail;
    }
    std::fclose(fp);
    return value;
fail:
    std::fclose(fp);
    return -1;
}
