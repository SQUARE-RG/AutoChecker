#include <cstdio>

int summarizeFile() {
    std::FILE* fp = std::fopen("numbers.txt", "r");
    if (fp == nullptr) {
        return -1;
    }

    int value = 0;
    while (std::fscanf(fp, "%d", &value) == 1) {
        if (value < 0) {
            break;
        }
    }

    return std::ferror(fp) ? -2 : 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-10]
}

int main() {
    return summarizeFile();
}
