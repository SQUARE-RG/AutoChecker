#include <cstdio>

extern "C" char *gets(char *);

int main()
{
    char buffer[16] = {0};
    do {
        std::printf("Input: ");
    } while (gets(buffer) != nullptr); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
    std::printf("The line entered was:%s\n", buffer);
    return 0;
}
