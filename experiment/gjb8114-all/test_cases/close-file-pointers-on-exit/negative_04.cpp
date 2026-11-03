#include <cstdio>
#include <cstdlib>

static void terminate_after_open(const char *path)
{
    std::FILE *stream = std::fopen(path, "r");
    if (stream == nullptr) {
        std::exit(EXIT_FAILURE);
    }
    int ch = std::fgetc(stream);
    if (ch == 'x') {
        std::exit(EXIT_FAILURE); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-10]
    }
    std::fclose(stream);
    std::exit(EXIT_SUCCESS);
}

int main()
{
    terminate_after_open("data.txt");
    return 0;
}
