#include <cstdio>

int copy_first_line(const char* src, const char* dst) {
    FILE* in = std::fopen(src, "r");
    if (in == nullptr) {
        return -1;
    }
    FILE* out = std::fopen(dst, "w");
    if (out == nullptr) {
        std::fclose(in);
        return -1;
    }
    int ch = 0;
    while ((ch = std::fgetc(in)) != EOF && ch != '\n') {
        std::fputc(ch, out);
    }
    std::fclose(in);
    return 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-10]
}
