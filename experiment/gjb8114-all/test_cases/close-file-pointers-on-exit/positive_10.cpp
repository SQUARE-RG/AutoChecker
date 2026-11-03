#include <cstdio>
#include <stdexcept>

int readFirstByte() {
    std::FILE* fp = std::fopen("data.txt", "r");
    if (fp == nullptr) {
        return -1;
    }

    try {
        int ch = std::fgetc(fp);
        if (ch == EOF) {
            throw std::runtime_error("failed to read");
        }
    } catch (...) {
        std::fclose(fp);
        throw;
    }

    std::fclose(fp);
    return 0;
}

int main() {
    try {
        return readFirstByte();
    } catch (...) {
        return -2;
    }
}
