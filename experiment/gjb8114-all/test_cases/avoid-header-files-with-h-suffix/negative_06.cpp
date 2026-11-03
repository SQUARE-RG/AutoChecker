#include <ctype.h>  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-4]

int main() {
    int result = isalpha('A');
    return result > 0 ? 0 : 1;
}
