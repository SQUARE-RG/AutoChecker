#include <cstdio>
#include <stdexcept>

int read_with_exception(bool fail)
{
    std::FILE* fp = std::fopen("data.txt", "r");
    if (fp == nullptr) {
        return -1;
    }

    try {
        if (fail) {
            throw std::runtime_error("simulated read failure");
        }
        char buffer[64];
        std::fgets(buffer, sizeof(buffer), fp);
        std::fclose(fp);
        return 0;
    } catch (const std::runtime_error&) {
        return -2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-10]
    }
}

int main()
{
    return read_with_exception(true);
}
