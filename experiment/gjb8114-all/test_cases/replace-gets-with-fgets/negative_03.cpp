#include <cstdio>

extern "C" char *gets(char *);

static char *read_line(char *buffer)
{
    return gets(buffer); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
}

int main()
{
    char line[8] = {0};
    if (read_line(line) == nullptr) {
        std::printf("read error\n");
        return 1;
    }
    std::printf("line: %s\n", line);
    return 0;
}
