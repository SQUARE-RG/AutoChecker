#include <cstddef>

int main()
{
    int value = 0;
    int* p = &value;
    int result = 0;
    switch (p == nullptr) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
        case true:
            result = 1;
            break;
        case false:
            result = 2;
            break;
    }
    return result;
}
