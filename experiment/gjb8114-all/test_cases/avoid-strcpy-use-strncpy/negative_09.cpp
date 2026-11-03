#include <cstring>

namespace st = std;

void copy_serial(char (&destination)[20], const char* source) {
    st::strcpy(destination, source); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
}
