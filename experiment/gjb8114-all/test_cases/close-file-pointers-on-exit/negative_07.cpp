#include <cstdio>

int process_file(int mode)
{
    std::FILE* fp = std::fopen("data.txt", "r");
    if (fp == nullptr) {
        return -1;
    }

    char buffer[64];
    if (std::fgets(buffer, sizeof(buffer), fp) == nullptr) {
        std::fclose(fp);
        return -2;
    }

    switch (mode) {
    case 0:
        return 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-10]
    default:
        std::fclose(fp);
        return 0;
    }
}

int main()
{
    return process_file(0);
}
