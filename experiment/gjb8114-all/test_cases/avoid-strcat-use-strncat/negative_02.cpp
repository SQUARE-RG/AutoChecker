#include <string.h>

void join_name(char* dest, const char* name) {
    strcat(dest, name); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
}

int main() {
    char buffer[64] = "user:";
    join_name(buffer, "alice");
    return 0;
}
