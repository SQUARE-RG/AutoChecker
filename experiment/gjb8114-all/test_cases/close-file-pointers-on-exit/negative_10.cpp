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
        throw; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-10]
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
