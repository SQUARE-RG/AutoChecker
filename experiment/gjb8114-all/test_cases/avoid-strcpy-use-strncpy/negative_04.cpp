#include <string.h>
#include <string>

int main() {
    std::string source = "portable";
    char destination[16]{};
    ::strcpy(destination, source.c_str()); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
    return destination[0] == 'p' ? 0 : 1;
}
